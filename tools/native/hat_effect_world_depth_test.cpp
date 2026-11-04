/* Real DX9Ex pixel tests for the same import-free isolation implementation. */
#include <windows.h>
#include <d3d9.h>
#include <cstdio>
#include <cstdlib>
#define HAT_DEPTH_TEST
#include "hat_effect_world_depth.cpp"

static IDirect3DDevice9Ex* gpu;
static IDirect3DSurface9* color;
static IDirect3DSurface9* readback;
static unsigned char renderer[0x300];
static unsigned char stateCache[0x600];
static unsigned char polygon[0xA8];
static u32 scope = 1;
static float drawZ = 0.5f;
static float drawLeft = 0, drawRight = 64;
static u32 drawColor = 0xFF00FF00;
static unsigned cases = 0;
static bool replayMutation = false;

static void require(bool ok, const char* message) {
	if (!ok) { std::fprintf(stderr, "FAIL: %s\n", message); std::exit(1); }
}
static void hr(HRESULT value, const char* label) {
	if (FAILED(value)) { std::fprintf(stderr, "%s HRESULT=%08lX\n", label, static_cast<unsigned long>(value)); std::exit(1); }
}
struct Vertex { float x, y, z, rhw; u32 color; };
static void rectangle(float x, float right, float depth, u32 tint) {
	Vertex v[] = {{x - .5f, -.5f, depth, 1, tint}, {right - .5f, -.5f, depth, 1, tint},
		{x - .5f, 63.5f, depth, 1, tint}, {right - .5f, 63.5f, depth, 1, tint}};
	hr(gpu->SetFVF(D3DFVF_XYZRHW | D3DFVF_DIFFUSE), "FVF");
	hr(gpu->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP, 2, v, sizeof(Vertex)), "DrawPrimitiveUP");
}
static void __fastcall drawNative(Ptr, Ptr, Ptr) {
	rectangle(drawLeft, drawRight, drawZ, drawColor);
}
static void __fastcall world1(Ptr, Ptr) {
	// Opaque wall in front on the left; remote geometry behind on the right.
	if (HatDepthDiagnostics.inReplay) {
		if (replayMutation) {
			// Simulate native material/cache updates during world replay.
			stateCache[0x20] = 0xCC;
			field(renderer, 0x268) = 0xBAD00001;
			hr(gpu->SetRenderState(D3DRS_COLORWRITEENABLE, 15), "Replay material color");
		}
		drawColor = 0xFF0000FF;
		drawZ = .2f;
		drawLeft = 0; drawRight = 32;
		HatDepthDraw40(renderer, nullptr, polygon);
		drawZ = .9f; drawLeft = 32; drawRight = 64;
		HatDepthDraw40(renderer, nullptr, polygon);
		drawLeft = 0; drawRight = 64;
	} else {
		rectangle(0, 32, .2f, 0xFF0000FF);
		rectangle(32, 64, .9f, 0xFF0000FF);
	}
}
static void __fastcall world2(Ptr, Ptr) {}
static void __fastcall world3(Ptr, Ptr) {}

static u32 pixel(unsigned x) {
	hr(gpu->GetRenderTargetData(color, readback), "Readback");
	D3DLOCKED_RECT lock;
	hr(readback->LockRect(&lock, nullptr, D3DLOCK_READONLY), "LockRect");
	u32 value = *reinterpret_cast<u32*>(static_cast<u8*>(lock.pBits) + 32 * lock.Pitch + x * 4);
	hr(readback->UnlockRect(), "UnlockRect");
	return value & 0xFFFFFF;
}
static void states() {
	hr(gpu->SetRenderState(D3DRS_ZENABLE, TRUE), "Z on");
	hr(gpu->SetRenderState(D3DRS_ZWRITEENABLE, TRUE), "Z write");
	hr(gpu->SetRenderState(D3DRS_ZFUNC, D3DCMP_LESSEQUAL), "Z func");
	hr(gpu->SetRenderState(D3DRS_COLORWRITEENABLE, 15), "Color write");
	hr(gpu->SetRenderState(D3DRS_CULLMODE, D3DCULL_NONE), "Cull");
	hr(gpu->SetRenderState(D3DRS_LIGHTING, FALSE), "Lighting");
	hr(gpu->SetRenderState(D3DRS_ALPHABLENDENABLE, FALSE), "Blend");
	hr(gpu->SetTexture(0, nullptr), "Texture");
}
static void scene(bool before, float playerZ, float effectZ, bool failCapture, bool tagged, bool use40 = false) {
	states();
	hr(gpu->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER, 0xFF000000, 1, 0), "Clear");
	hr(gpu->BeginScene(), "BeginScene");
	world1(nullptr, nullptr);
	HatDepthDiagnostics.frameActive = 1;
	HatDepthDiagnostics.ready = 0;
	byteField(polygon, 0x15) = 0;
	if (tagged) HatDepthMark(polygon, polygon);
	const u8 cacheBefore = stateCache[0x20];
	const u32 textureBefore = field(renderer, 0x268);
	if (!failCapture) HatDepthCapture(renderer);
	if (tagged && !failCapture) require(HatDepthDiagnostics.ready == 1, "World capture ready");
	require(stateCache[0x20] == cacheBefore && field(renderer, 0x268) == textureBefore, "Native state and texture caches restored");
	DWORD value = 0;
	hr(gpu->GetRenderState(D3DRS_COLORWRITEENABLE, &value), "Capture restores color state"); require(value == 15, "Capture color mask restored");
	// Capture must never alter the visible world colors.
	// Character alpha-test prepass writes nearer player depth, without color.
	hr(gpu->SetRenderState(D3DRS_COLORWRITEENABLE, 0), "Character prepass color");
	rectangle(0, 64, playerZ, 0xFFFF0000);
	hr(gpu->SetRenderState(D3DRS_COLORWRITEENABLE, 15), "Character color");
	hr(gpu->SetRenderState(D3DRS_ZWRITEENABLE, FALSE), "Color pass Z write off");
	drawZ = effectZ; drawColor = 0xFF00FF00;
	if (before) {
		if (use40) HatDepthDraw40(renderer, nullptr, polygon);
		else HatDepthDraw32(renderer, nullptr, polygon);
	}
	rectangle(0, 64, playerZ, 0xFFFF0000);
	if (!before) {
		if (use40) HatDepthDraw40(renderer, nullptr, polygon);
		else HatDepthDraw32(renderer, nullptr, polygon);
	}
	hr(gpu->GetRenderState(D3DRS_ZENABLE, &value), "State restore Z"); require(value == 1, "Z state restored");
	hr(gpu->GetRenderState(D3DRS_ZWRITEENABLE, &value), "State restore write"); require(value == 0, "Z write restored");
	Ptr surface = nullptr;
	hr(gpu->GetDepthStencilSurface(reinterpret_cast<IDirect3DSurface9**>(&surface)), "Main surface");
	require(surface != worldDepth, "Main depth surface restored"); release(surface);
	hr(gpu->EndScene(), "EndScene");
	const bool visible = !before && tagged;
	require(pixel(48) == (visible ? 0x00FF00u : 0xFF0000u), "After effect ignores nearer player; before effect stays behind");
	require(pixel(16) == ((!before && tagged && failCapture) ? 0x00FF00u : 0xFF0000u), "Opaque wall clips only with successful capture");
	HatDepthDiagnostics.frameActive = 0;
	++cases;
}
static void worldOnly() {
	states();
	hr(gpu->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER, 0xFF000000, 1, 0), "Clear world test");
	hr(gpu->BeginScene(), "Begin world test");
	world1(nullptr, nullptr);
	HatDepthDiagnostics.frameActive = 1;
	HatDepthMark(polygon, polygon);
	HatDepthCapture(renderer);
	hr(gpu->SetRenderState(D3DRS_ZWRITEENABLE, FALSE), "World effect writes off");
	drawZ = .5f; drawColor = 0xFF00FF00;
	HatDepthDraw40(renderer, nullptr, polygon);
	hr(gpu->EndScene(), "End world test");
	require(pixel(16) == 0x0000FF && pixel(48) == 0x00FF00, "World mask clips without a player; replay does not repaint color");
	HatDepthDiagnostics.frameActive = 0;
	++cases;
}
static void __fastcall fakeFrame(Ptr, Ptr) {
	require(HatDepthDiagnostics.frameActive == 1, "Frame scope entered");
	HatDepthDiagnostics.ready = 1;
}
int main() {
	WNDCLASSW wc = {}; wc.lpfnWndProc = DefWindowProcW; wc.hInstance = GetModuleHandleW(nullptr); wc.lpszClassName = L"HatDepthTest";
	require(RegisterClassW(&wc) != 0, "RegisterClass");
	HWND window = CreateWindowW(wc.lpszClassName, L"HatEffect world depth tests", WS_OVERLAPPEDWINDOW,
		0, 0, 64, 64, nullptr, nullptr, wc.hInstance, nullptr);
	require(window != nullptr, "CreateWindow");
	IDirect3D9Ex* api = nullptr; hr(Direct3DCreate9Ex(D3D_SDK_VERSION, &api), "Direct3DCreate9Ex");
	D3DPRESENT_PARAMETERS pp = {}; pp.Windowed = TRUE; pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
	pp.hDeviceWindow = window; pp.BackBufferWidth = 64; pp.BackBufferHeight = 64; pp.BackBufferFormat = D3DFMT_X8R8G8B8;
	pp.EnableAutoDepthStencil = TRUE; pp.AutoDepthStencilFormat = D3DFMT_D24S8;
	hr(api->CreateDeviceEx(D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL, window,
		D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, nullptr, &gpu), "CreateDeviceEx");
	hr(gpu->GetRenderTarget(0, &color), "Render target");
	hr(gpu->CreateOffscreenPlainSurface(64, 64, D3DFMT_X8R8G8B8, D3DPOOL_SYSTEMMEM, &readback, nullptr), "Readback surface");
	field(renderer, 0) = 0xFD6D64; field(renderer, 0x260) = reinterpret_cast<u32>(gpu);
	field(renderer, 0x25C) = reinterpret_cast<u32>(stateCache);
	HatDepthConfig.scope = &scope; HatDepthConfig.rendererVtable = 0xFD6D64;
	HatDepthConfig.draw32 = reinterpret_cast<Draw>(drawNative); HatDepthConfig.draw40 = reinterpret_cast<Draw>(drawNative);
	HatDepthConfig.ground1 = reinterpret_cast<Method>(world1); HatDepthConfig.ground2 = reinterpret_cast<Method>(world2);
	HatDepthConfig.models = reinterpret_cast<Method>(world3);
	const float players[] = {.01f, .1f, .19f}, effects[] = {.3f, .5f, .8f};
	const bool formats[] = {false, true};
	for (bool use40 : formats) for (float player : players) for (float effect : effects) {
		scene(false, player, effect, false, true, use40);
		scene(true, player, effect, false, true, use40);
	}
	scene(false, .1f, .5f, true, true); // stock overlay fallback, never player clipping
	scene(false, .1f, .5f, false, false); // unrelated draw retains original actor-depth clipping
	replayMutation = true;
	scene(false, .1f, .5f, false, true);
	worldOnly();
	HatDepthRelease(); require(worldDepth == nullptr && !HatDepthDiagnostics.ready, "Release for reset");
	readback->Release(); color->Release();
	pp.BackBufferWidth = 80; pp.BackBufferHeight = 80;
	hr(gpu->ResetEx(&pp, nullptr), "ResetEx after releasing owned surface");
	hr(gpu->GetRenderTarget(0, &color), "Render target after reset");
	hr(gpu->CreateOffscreenPlainSurface(80, 80, D3DFMT_X8R8G8B8, D3DPOOL_SYSTEMMEM, &readback, nullptr), "Readback after reset");
	scene(false, .1f, .5f, false, true);
	require(description.width == 80 && description.height == 80, "Surface recreated at new resolution");
	++cases;
	HatDepthConfig.frame = reinterpret_cast<Method>(fakeFrame);
	HatDepthFrame(renderer, nullptr);
	require(!HatDepthDiagnostics.frameActive && !HatDepthDiagnostics.ready && queued == 0, "Frame scope and stale-ready state reset");
	++cases;
	HatDepthRelease();
	readback->Release(); color->Release(); gpu->Release(); api->Release(); DestroyWindow(window);
	std::printf("PASS %u real DX9Ex pixel/readback cases: world-only occlusion, both character layers, stock fallback, state/surface restore\n", cases);
	return 0;
}