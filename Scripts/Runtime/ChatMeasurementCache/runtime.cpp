// Copyright (c) 2026 Louis T Steinhil - Licensed under GNU GPL
// For more information, see LICENSE in the main folder

// Native measurement caching for 2025-07-16; no wrapping or tag decisions.
// Reference design: SCIEL & ICE, Cache_Fix.txt.
extern "C" long __cdecl _InterlockedCompareExchange(volatile long*, long, long);
#pragma intrinsic(_InterlockedCompareExchange)
#define CHAT_OFFSET(type, field) ((u32) & (((type*)0)->field))

// Profile constants remain fixed in the emitted client. The native Win32 host
// substitutes only its font boundary and backing globals at compile time.
#ifndef CHAT_NATIVE_WIDTH_ADDRESS
#define CHAT_NATIVE_WIDTH_ADDRESS 0x00A21C90u
#define CHAT_FONT_GLOBALS_ADDRESS 0x0159B800u
#define CHAT_FONT_MAP_ADDRESS 0x011DCF30u
#endif
typedef unsigned int u32;
typedef unsigned char u8;

struct Key {
	u32 painter, encoding, flavor, fontMode, language, codePage, fontMap[20];
};
struct AsciiEntry {
	u32 generation;
	int width;
};
struct TextEntry {
	u32 generation, length;
	int width;
	u8 text[256];
};
struct GlyphOwner {
	u32 owner;
	Key key;
	u32 generation, nextText;
	AsciiEntry ascii[128];
	TextEntry text[16];
};
struct FragmentEntry {
	u32 hash, length;
	int width;
	u8 text[512];
};
struct State {
	volatile long busy;
	u32 nextOwner;
	GlyphOwner owners[4];
	u32 fragmentOwner;
	Key fragmentKey;
	FragmentEntry fragments[32];
};
static_assert(sizeof(State) == 38596, "Native chat cache ABI changed");

extern "C" __declspec(dllexport) struct Api {
	State* state;
} ChatCacheApi = {};
extern "C" __declspec(dllexport) const u32 ChatCacheLayout[] = {sizeof(State), sizeof(Key),
	sizeof(GlyphOwner), sizeof(AsciiEntry), sizeof(TextEntry), sizeof(FragmentEntry),
	CHAT_OFFSET(State, owners), CHAT_OFFSET(State, fragmentOwner), CHAT_OFFSET(State, fragmentKey),
	CHAT_OFFSET(State, fragments), CHAT_OFFSET(GlyphOwner, generation), CHAT_OFFSET(GlyphOwner, nextText),
	CHAT_OFFSET(GlyphOwner, ascii), CHAT_OFFSET(GlyphOwner, text)};

static bool eligible(const void* owner) {
	if (!owner)
		return false;
	u32 vt = *(const u32*)owner;
	return vt == 0x0102D280 || vt == 0x0102D370 || vt == 0x0102D460;
}
static void capture(const void* owner, Key* key) {
	key->painter = *(const u32*)((u32)owner + 0x24);
	key->encoding = *(const u32*)(CHAT_FONT_GLOBALS_ADDRESS + 0x0C);
	key->flavor = key->encoding ? *(const unsigned short*)(key->encoding + 0xB4) : 0;
	key->fontMode = *(const u8*)(CHAT_FONT_GLOBALS_ADDRESS + 0xA4);
	key->language = *(const u32*)(CHAT_FONT_GLOBALS_ADDRESS + 0x10);
	key->codePage = *(const u32*)(CHAT_FONT_GLOBALS_ADDRESS + 0x18);
	for (u32 i = 0; i < 20; ++i)
		key->fontMap[i] = ((const u32*)CHAT_FONT_MAP_ADDRESS)[i];
}
static bool sameKey(const Key* a, const Key* b) {
	const u32* x = (const u32*)a;
	const u32* y = (const u32*)b;
	for (u32 i = 0; i < sizeof(Key) / 4; ++i)
		if (x[i] != y[i])
			return false;
	return true;
}
static void copyKey(Key* dest, const Key* source) {
	u32* x = (u32*)dest;
	const u32* y = (const u32*)source;
	for (u32 i = 0; i < sizeof(Key) / 4; ++i)
		x[i] = y[i];
}
static bool sameText(const u8* a, const u8* b, u32 length) {
	for (u32 i = 0; i < length; ++i)
		if (a[i] != b[i])
			return false;
	return true;
}
static void copyText(u8* dest, const u8* source, u32 length) {
	for (u32 i = 0; i < length; ++i)
		dest[i] = source[i];
}

// Keep native exception dispatch and SafeSEH tables unchanged. If measurement
// unwinds instead of returning, busy deliberately remains set: this process
// falls back to native measurement until restart, without reusing partial data.
typedef int(__thiscall* NativeWidth)(const void*, const u8*, u32, u32, u32, u32, u32);
static int native(
	const void* owner, const u8* text, u32 length, u32 style, u32 font, u32 bold, u32 options) {
	return ((NativeWidth)CHAT_NATIVE_WIDTH_ADDRESS)(
		owner, text, length, style, font, bold, options);
}

static void advance(GlyphOwner* context) {
	++context->generation;
	context->nextText = 0;
	if (context->generation)
		return;
	for (u32 i = 0; i < 128; ++i)
		context->ascii[i].generation = 0;
	for (u32 i = 0; i < 16; ++i)
		context->text[i].generation = 0;
	context->generation = 1;
}

// Returns zero only when the adapter must execute the displaced native block.
// The output is separate so zero/negative native widths keep their exact value.
extern "C" __declspec(dllexport) int __stdcall ChatGlyphWidth(
	const void* owner, const u8* text, u32 length, int* output) {
	State* state = ChatCacheApi.state;
	if (!state || !text || !output || length == 0 || length > 255 || !eligible(owner))
		return 0;
	if (_InterlockedCompareExchange(&state->busy, 1, 0))
		return 0;
	Key key;
	capture(owner, &key);
	GlyphOwner* context = 0;
	for (u32 i = 0; i < 4; ++i) {
		if (state->owners[i].owner == (u32)owner) {
			context = &state->owners[i];
			break;
		}
	}
	if (!context) {
		for (u32 i = 0; i < 4; ++i) {
			if (!state->owners[i].owner) {
				context = &state->owners[i];
				break;
			}
		}
		if (!context)
			context = &state->owners[state->nextOwner++ & 3];
	}
	if (context->owner != (u32)owner || !sameKey(&context->key, &key)) {
		context->owner = (u32)owner;
		copyKey(&context->key, &key);
		advance(context);
	}
	AsciiEntry* ascii = 0;
	if (length == 1 && text[0] < 128) {
		ascii = &context->ascii[text[0]];
		if (ascii->generation == context->generation) {
			*output = ascii->width;
			state->busy = 0;
			return 1;
		}
	} else {
		for (u32 i = 0; i < 16; ++i) {
			TextEntry* entry = &context->text[i];
			if (entry->generation == context->generation && entry->length == length &&
				sameText(entry->text, text, length)) {
				*output = entry->width;
				state->busy = 0;
				return 1;
			}
		}
	}
	int width = native(owner, text, length, 0, 12, 0, 0);
	Key after;
	capture(owner, &after);
	if (width > 0 && sameKey(&key, &after)) {
		if (ascii) {
			ascii->width = width;
			ascii->generation = context->generation;
		} else {
			TextEntry* entry = &context->text[context->nextText++ & 15];
			entry->generation = 0;
			copyText(entry->text, text, length);
			entry->length = length;
			entry->width = width;
			entry->generation = context->generation;
		}
	}
	*output = width;
	state->busy = 0;
	return 1;
}

// Fastcall's ECX receiver and six stack arguments match the original thiscall.
extern "C" __declspec(dllexport) int __fastcall ChatFragmentWidth(const void* owner, void*,
	const u8* text, u32 length, u32 style, u32 font, u32 bold, u32 options) {
	State* state = ChatCacheApi.state;
	if (!state || !text || length || style || font != 12 || bold || options || !eligible(owner))
		return native(owner, text, length, style, font, bold, options);
	u32 size = 0, hash = 2166136261u;
	for (; size < 512 && text[size]; ++size)
		hash = (hash ^ text[size]) * 16777619u;
	if (!size || size == 512)
		return native(owner, text, length, style, font, bold, options);
	if (_InterlockedCompareExchange(&state->busy, 1, 0))
		return native(owner, text, length, style, font, bold, options);
	Key key;
	capture(owner, &key);
	if (state->fragmentOwner != (u32)owner || !sameKey(&state->fragmentKey, &key)) {
		for (u32 i = 0; i < 32; ++i)
			state->fragments[i].width = 0;
		state->fragmentOwner = (u32)owner;
		copyKey(&state->fragmentKey, &key);
	}
	FragmentEntry* entry = &state->fragments[hash & 31];
	if (entry->width > 0 && entry->hash == hash && entry->length == size &&
		sameText(entry->text, text, size)) {
		int width = entry->width;
		state->busy = 0;
		return width;
	}
	int width = native(owner, text, length, style, font, bold, options);
	Key after;
	capture(owner, &after);
	if (width > 0 && sameKey(&key, &after)) {
		entry->width = 0;
		copyText(entry->text, text, size);
		entry->hash = hash;
		entry->length = size;
		entry->width = width;
	}
	state->busy = 0;
	return width;
}
