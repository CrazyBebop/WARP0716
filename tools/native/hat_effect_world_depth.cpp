/* 2025-07-16 DX9Ex HatEffect world-only depth isolation. No imports or DLL.
 * Native world queues are replayed with color writes disabled before the
 * character prepass. Only tagged HatEffect color draws switch depth surfaces.
 * Native actor depth, queues, blend/material state and resource ownership stay
 * unchanged. Legacy DX7 is deliberately stock, not claimed as supported.
 */
using u8 = unsigned char;
using u32 = unsigned int;
using s32 = int;
using Ptr = void*;
using Method = void (__thiscall*)(Ptr);
using Draw = void (__thiscall*)(Ptr, Ptr);
#ifndef HAT_DEPTH_TEST
extern "C" { int _fltused = 0; }
#endif

struct Desc {
	u32 format, type, usage, pool, multisample, quality, width, height;
};
struct Configuration {
	u32* scope;
	Draw draw32;
	Draw draw40;
	Method frame;
	Method ground1;
	Method ground2;
	Method models;
	u32 rendererVtable;
};
struct Diagnostics {
	u32 tagged, captures, captureFailures, worldDraws, stockFallbacks;
	u32 releases, inReplay, ready, frameActive;
	s32 lastError;
};
extern "C" {
__declspec(dllexport) Configuration HatDepthConfig = {};
__declspec(dllexport) Diagnostics HatDepthDiagnostics = {};
}
static Ptr worldDepth = nullptr;
static Ptr ownerDevice = nullptr;
static Desc description = {};
static u32 queued = 0;
static constexpr u8 Tag = 0xA7;

template <typename Fn> static Fn method(Ptr object, u32 slot) {
	return reinterpret_cast<Fn>((*static_cast<Ptr**>(object))[slot]);
}
static u32& field(Ptr p, u32 offset) {
	return *reinterpret_cast<u32*>(static_cast<u8*>(p) + offset);
}
static u8& byteField(Ptr p, u32 offset) {
	return *(static_cast<u8*>(p) + offset);
}
static void release(Ptr p) {
	if (p) method<u32 (__stdcall*)(Ptr)>(p, 2)(p);
}
static s32 getState(Ptr device, u32 state, u32* value) {
	return method<s32 (__stdcall*)(Ptr, u32, u32*)>(device, 58)(device, state, value);
}
static s32 setState(Ptr device, u32 state, u32 value) {
	return method<s32 (__stdcall*)(Ptr, u32, u32)>(device, 57)(device, state, value);
}
static s32 getDepth(Ptr device, Ptr* surface) {
	return method<s32 (__stdcall*)(Ptr, Ptr*)>(device, 40)(device, surface);
}
static s32 setDepth(Ptr device, Ptr surface) {
	return method<s32 (__stdcall*)(Ptr, Ptr)>(device, 39)(device, surface);
}
static bool dx9(Ptr renderer) {
	return renderer && field(renderer, 0) == HatDepthConfig.rendererVtable;
}
static bool same(const Desc& a, const Desc& b) {
	return a.width == b.width && a.height == b.height && a.format == b.format &&
		a.multisample == b.multisample && a.quality == b.quality;
}
extern "C" __declspec(dllexport) void __cdecl HatDepthRelease() {
	release(worldDepth);
	if (worldDepth) ++HatDepthDiagnostics.releases;
	worldDepth = nullptr;
	ownerDevice = nullptr;
	HatDepthDiagnostics.ready = 0;
}
extern "C" __declspec(dllexport) void __cdecl HatDepthMark(Ptr polygon, Ptr primitive) {
	if (!HatDepthConfig.scope || !*HatDepthConfig.scope || !polygon || !primitive)
		return;
	// +15 is initialized to zero by CPoly's native pool reset (005601B8).
	// These HatEffect queues do not participate in the character depth prepass.
	byteField(polygon, 0x15) = Tag;
	++queued;
	++HatDepthDiagnostics.tagged;
}
extern "C" __declspec(dllexport) void __cdecl HatDepthCapture(Ptr renderer) {
	HatDepthDiagnostics.ready = 0;
	if (!dx9(renderer) || !queued || !HatDepthDiagnostics.frameActive)
		return;
	Ptr device = reinterpret_cast<Ptr>(field(renderer, 0x260));
	Ptr mainDepth = nullptr, states = nullptr;
	Desc desc = {};
	s32 status = getDepth(device, &mainDepth);
	if (status >= 0 && mainDepth)
		status = method<s32 (__stdcall*)(Ptr, Desc*)>(mainDepth, 12)(mainDepth, &desc);
	if (status >= 0 && mainDepth) {
		if (ownerDevice != device || !same(description, desc)) HatDepthRelease();
		if (!worldDepth) {
			// Matching format, dimensions and multisampling; non-discardable.
			status = method<s32 (__stdcall*)(Ptr, u32, u32, u32, u32, u32, s32, Ptr*, Ptr)>(device, 29)(
				device, desc.width, desc.height, desc.format, desc.multisample, desc.quality, 0, &worldDepth, nullptr);
			if (status >= 0 && worldDepth) { ownerDevice = device; description = desc; }
		}
		if (status >= 0 && worldDepth)
			status = method<s32 (__stdcall*)(Ptr, u32, Ptr*)>(device, 59)(device, 1, &states);
	}
	if (status >= 0 && worldDepth && states) {
		u32 savedCache[0x4C0 / 4];
		u32* cache = reinterpret_cast<u32*>(field(renderer, 0x25C) + 0x0C + 8);
		for (u32 i = 0; i < 0x4C0 / 4; ++i) savedCache[i] = cache[i];
		status = setDepth(device, worldDepth);
		if (status >= 0)
			status = method<s32 (__stdcall*)(Ptr, u32, Ptr, u32, u32, float, u32)>(device, 43)(device, 0, nullptr, 2, 0, 1.0f, 0);
		if (status >= 0) status = setState(device, 7, 1);   // ZENABLE
		if (status >= 0) status = setState(device, 14, 1);  // ZWRITEENABLE
		if (status >= 0) status = setState(device, 23, 4);  // LESSEQUAL
		if (status >= 0) status = setState(device, 168, 0); // COLORWRITEENABLE
		if (status >= 0) {
			const u32 texture0 = field(renderer, 0x268), texture1 = field(renderer, 0x26C);
			const u32 texture2 = field(renderer, 0x270);
			HatDepthDiagnostics.inReplay = 1;
			HatDepthConfig.ground1(renderer);
			HatDepthConfig.ground2(renderer);
			HatDepthConfig.models(renderer);
			HatDepthDiagnostics.inReplay = 0;
			field(renderer, 0x268) = texture0;
			field(renderer, 0x26C) = texture1;
			field(renderer, 0x270) = texture2;
			HatDepthDiagnostics.ready = 1;
			++HatDepthDiagnostics.captures;
		}
		// Native passes update their own state cache even when the GPU state
		// block later restores the device. Keep those two views synchronized.
		for (u32 i = 0; i < 0x4C0 / 4; ++i) cache[i] = savedCache[i];
	}
	if (mainDepth) {
		if (setDepth(device, mainDepth) < 0) HatDepthDiagnostics.ready = 0;
		release(mainDepth);
	}
	if (states) {
		if (method<s32 (__stdcall*)(Ptr)>(states, 5)(states) < 0) HatDepthDiagnostics.ready = 0;
		release(states);
	}
	if (!HatDepthDiagnostics.ready) {
		++HatDepthDiagnostics.captureFailures;
		HatDepthDiagnostics.lastError = status;
	}
}
static void draw(Ptr renderer, Ptr polygon, Draw stock) {
	if (!dx9(renderer) || !polygon) { stock(renderer, polygon); return; }
	Ptr device = reinterpret_cast<Ptr>(field(renderer, 0x260));
	if (HatDepthDiagnostics.inReplay) {
		// Enforce color suppression at the actual native draw boundary as well
		// as around the pass, even if a material changed it during replay.
		if (setState(device, 168, 0) >= 0 && setState(device, 7, 1) >= 0 &&
			setState(device, 14, 1) >= 0 && setState(device, 23, 4) >= 0)
			stock(renderer, polygon);
		return;
	}
	if (byteField(polygon, 0x15) != Tag) { stock(renderer, polygon); return; }
	u32 enabled = 1, writes = 0, compare = 4;
	if (getState(device, 7, &enabled) < 0 || getState(device, 14, &writes) < 0 ||
		getState(device, 23, &compare) < 0) { ++HatDepthDiagnostics.stockFallbacks; return; }
	Ptr previous = nullptr;
	bool isolated = false;
	if (HatDepthDiagnostics.ready && worldDepth && getDepth(device, &previous) >= 0 && previous)
		isolated = setDepth(device, worldDepth) >= 0;
	const s32 z = setState(device, 7, isolated ? 1 : 0);
	const s32 w = setState(device, 14, 0);
	const s32 f = setState(device, 23, 4);
	if (z >= 0 && w >= 0 && f >= 0) {
		stock(renderer, polygon);
		if (isolated) ++HatDepthDiagnostics.worldDraws;
		else ++HatDepthDiagnostics.stockFallbacks;
	}
	if (previous) { setDepth(device, previous); release(previous); }
	setState(device, 7, enabled);
	setState(device, 14, writes);
	setState(device, 23, compare);
}
extern "C" __declspec(dllexport) void __fastcall HatDepthDraw32(Ptr renderer, Ptr, Ptr polygon) {
	draw(renderer, polygon, HatDepthConfig.draw32);
}
extern "C" __declspec(dllexport) void __fastcall HatDepthDraw40(Ptr renderer, Ptr, Ptr polygon) {
	draw(renderer, polygon, HatDepthConfig.draw40);
}
extern "C" __declspec(dllexport) void __fastcall HatDepthFrame(Ptr renderer, Ptr) {
	HatDepthDiagnostics.ready = 0;
	HatDepthDiagnostics.frameActive = 1;
	HatDepthConfig.frame(renderer);
	HatDepthDiagnostics.frameActive = 0;
	HatDepthDiagnostics.ready = 0;
	queued = 0;
}
extern "C" void HatDepthEntry() {}