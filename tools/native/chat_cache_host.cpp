// Copyright (c) 2026 Louis T Steinhil - Licensed under GNU GPL
// For more information, see LICENSE in the main folder

// Execute the production cache on Win32; replace only the native font boundary.
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <windows.h>

static int __fastcall width(
	const void*, void*, const unsigned char*, unsigned, unsigned, unsigned, unsigned, unsigned);
static unsigned fontGlobals[64] = {}, fontMap[20] = {};
#define CHAT_NATIVE_WIDTH_ADDRESS reinterpret_cast<std::size_t>(&width)
#define CHAT_FONT_GLOBALS_ADDRESS reinterpret_cast<std::size_t>(fontGlobals)
#define CHAT_FONT_MAP_ADDRESS reinterpret_cast<std::size_t>(fontMap)
#include "../../Scripts/Runtime/ChatMeasurementCache/runtime.cpp"

static unsigned nativeWidths = 0;
static bool unwindNative = false;

static void require(bool value, const char* text) {
	if (!value) {
		std::fprintf(stderr, "FAIL %s\n", text);
		std::exit(1);
	}
}

static int __fastcall width(const void*, void*, const unsigned char* text, unsigned length,
	unsigned, unsigned, unsigned, unsigned) {
	++nativeWidths;
	if (unwindNative)
		RaiseException(0xE0422026, 0, 0, nullptr);
	return static_cast<int>(
		(length ? length : std::strlen(reinterpret_cast<const char*>(text))) * 7);
}

static int message(const void* owner, bool cached) {
	const u8* text = reinterpret_cast<const u8*>("repeat combat message");
	int total = 0;
	for (unsigned i = 0; text[i]; ++i) {
		int result = 0;
		if (!cached || !ChatGlyphWidth(owner, text + i, 1, &result))
			result = width(owner, nullptr, text + i, 1, 0, 12, 0, 0);
		total += result;
	}
	return total + (cached ? ChatFragmentWidth(owner, nullptr, text, 0, 0, 12, 0, 0)
		: width(owner, nullptr, text, 0, 0, 12, 0, 0));
}

int main() {
	static State state = {};
	ChatCacheApi.state = &state;
	unsigned char owner[256] = {};
	*reinterpret_cast<unsigned*>(owner) = 0x102D280;
	const u8* text = reinterpret_cast<const u8*>("fragment");
	for (unsigned i = 0; i < 2; ++i)
		require(ChatFragmentWidth(owner, nullptr, text, 0, 0, 12, 0, 0) == 56,
			"cold fragment-only traffic preserves width");
	require(nativeWidths == 1, "fragment cache works without append/bootstrap traffic");
	state = {};
	nativeWidths = 0;
	for (unsigned i = 0; i < 200; ++i)
		require(message(owner, true) == 294, "cached native width");
	const unsigned cachedCalls = nativeWidths;
	nativeWidths = 0;
	for (unsigned i = 0; i < 200; ++i)
		require(message(owner, false) == 294, "uncached native width");
	const unsigned originalCalls = nativeWidths;
	require(cachedCalls < originalCalls / 10, "bounded cache reduces native calls");
	unsigned before = nativeWidths;
	++fontGlobals[4];
	require(message(owner, true) == 294 && nativeWidths > before, "font context invalidates");
	state.busy = 1;
	int output = 0;
	require(!ChatGlyphWidth(owner, text, 1, &output), "busy glyph falls back");
	before = nativeWidths;
	require(ChatFragmentWidth(owner, nullptr, text, 0, 0, 12, 0, 0) == 56 &&
			nativeWidths == before + 1,
		"busy fragment follows native path");
	state = {};
	unwindNative = true;
	bool caught = false;
	__try {
		ChatGlyphWidth(owner, text, 1, &output);
	} __except (GetExceptionCode() == 0xE0422026 ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
		caught = true;
	}
	unwindNative = false;
	require(caught && state.busy == 1 && !ChatGlyphWidth(owner, text, 1, &output),
		"native SEH unwind disables reuse of partial state");
	ChatCacheApi.state = nullptr;
	require(!ChatGlyphWidth(owner, text, 1, &output), "missing state follows native path");
	require(ChatFragmentWidth(owner, nullptr, text, 0, 0, 12, 0, 0) == 56,
		"missing fragment state preserves width");
	std::printf("PASS native Win32 cache: identical widths, cold fragment, invalidation, "
		"busy fallback, SEH unwind; native calls cache-on=%u cache-off=%u\n",
		cachedCalls, originalCalls);
	return 0;
}
