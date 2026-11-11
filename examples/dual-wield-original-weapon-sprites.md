# Original dual/off-hand weapon sprites

For **2025-07-16 Ragexe 175220998**, this patch preserves original dagger, one-handed sword and axe artwork while dual wielding or using only an off-hand weapon.

## Required files

| File | Purpose |
|---|---|
| `Scripts/Patches/AllowDualWeaponSprites.qjs` | Canonical implementation: validates the client, owns resources, loads the bundles and installs three hooks |
| `Patches/Special.yml` | Registers the same exported patch name |
| `Inputs/DualWeaponRuntime/compositor.dwcp` | Compiled weapon compositor and placement data |
| `Inputs/DualWeaponRuntime/legacy-support.dwls` | Rebuildable 1,452-byte v2 bundle containing only the unchanged depth helper |
| `Inputs/DualWeaponRuntime/dual_weapon_male_assets.grf` | Missing original-weapon resources for both genders |
| `Inputs/DualWeaponRuntime/embedded-grfs-20250716.ini` | Example archive list for the tested GRFsEmbedded installation |

**The QJS is not standalone.** It reads both binary bundles before writing hooks. Omitting either causes validation to fail. The compatibility GRF supplies missing job filenames; omitting it can restore generic fallback artwork for affected weapons.

Keep the directory structure when installing into WARP. Copy the GRF into the client directory and register it at highest priority in the loader the EXE actually uses. The example INI requires the named base archives to exist. With GRFsEmbedded, select the matching archive list when repatching; DATA.INI alone does not change the embedded list.

Apply to a source with stock dual-weapon hook bytes, preserving other patch selections through the WARP session. Occupied hooks are rejected.

The full implementation retains the original `AllowDualWeaponSprites` name.
It is now the only patch filename, export and catalog entry. The temporary
custom-name wrapper has been removed at the user's request. External profiles
and saved sessions using `AllowDualCustomWeaponSprites` must change that selection
to `AllowDualWeaponSprites`. No alias or implicit migration remains. The patch-time
diagnostic event also uses `AllowDualWeaponSprites.AuthoredRig`.

Before allocating or writing dual-weapon hooks, the patch now checks the active
embedded/INI configuration and requires the compatibility GRF at highest priority
and present beside the target EXE. An inactive DATA.INI does not satisfy an embedded
configuration. Unknown reopened loaders fail with a clear instruction to reapply
GRFsEmbedded or GRFsFromIni. Runtime INI changes after patching remain the operator's
responsibility.

## Scope and fixes

Both genders of Assassin, High Assassin, Assassin Cross, Guillotine Cross and Shadow Cross have independent body profiles. The audited set covers **24 non-Drake views: 1/2/6, 31–47 and 58–61**. Other classes, unregistered views, custom body replacements and the 2026 client are outside this profile.

The patch fixes:

- The filename/export/YAML mismatch that could silently skip patch application.
- Stale custom resources after shields, unequips and failed/partial loads.
- Generic fallback accepted as an original resource: both ACT/SPR names now match the actual Lua suffix.
- Dagger/dagger and off-only placement, using anatomical equipment slots instead of treating native channels 5/6 as hands.
- Independent male/female Main Gauche, Stiletto and Gladius asset gaps, female view/body restrictions, missing axes and Shadow Cross aliases.
- Dead ECX receiver assignments in native item lookup calls and writable state sharing executable pages.

The archive keeps its historical male filename but contains **60 entries for both genders**. Donor SPR pixels are unchanged; compatibility ACT timelines are authored.

Held actions 32–39 use body/image-specific hand–hilt contacts. Dual attacks 88–95 preserve the accepted generic trajectory and select the corresponding individual source cell, including solo actions 80–87 where required. Other off-only phases retain native ACT transfer. The accepted compositor remains byte-identical after cleanup.

## Verification and source reference

This PR now includes the runtime generator, readable compositor C source, frozen
profile headers, canonical rig/grip inputs and depth-helper C++/inline-assembly
source. The build does not need a private client installation, evidence directory,
Git history, or a download from the source snapshot.

```text
python -m pip install -r tools/requirements-dual-weapon.txt
python tools/build_dual_weapon_runtime.py --check
python tools/build_dual_weapon_runtime.py --write
```

The two optional regression runners are retained in the immutable
[pre-cleanup tooling snapshot](https://github.com/YlenXWalker/WARP0716/tree/b8451c88d6a6a371e2bfa0e8b6dd8a22870edf49/tools). They are not build or patch-time dependencies. The current package keeps the complete source rebuild and `--check` path requested in [the maintainer review](https://github.com/CrazyBebop/WARP0716/pull/69#issuecomment-6330606195).

Use **MSVC toolset 14.51.36231 Hostx64/x86**, `cl` **19.51.36260** and linker
**14.51.36260.0**. `--tool-dir` locates that same toolset elsewhere.
`Inputs/DualWeaponRuntime/build.json` pins the compiler/backend/linker hashes,
normalized source hashes and exact outputs. `--check` compiles into temporary
storage, compares both bundles byte-for-byte, and never overwrites them. The only
normalized container bytes are the identified non-executable PE export/debug build
identity fields historically carried inside DWCP. Code, data, exports and
relocations are rebuilt from source.

DWLS v2 removes the retired capture core and old authoring rig; neither was injected
by the current renderer. Its 1,380-byte depth helper and all three relocation pairs
are identical to v1. The source preserves that helper's audited x86 instruction
order inside a naked C++ function so it can be assembled/rebuilt, rather than
shipping an opaque machine-code array. V1 inputs remain readable. The old complete
bundle and broader authoring/evidence history remain recoverable at
[`bf7bb2ad`](https://github.com/YlenXWalker/WARP0716/tree/bf7bb2ad16bded390bac67b0e3dfca57d831e311).

The [detailed reference](https://github.com/YlenXWalker/WARP0716/blob/f2a3a710f96fd8f1f705d8f7fd5ab19462a321a7/docs/dual-wield-original-weapon-sprites.md) records the view list, native ABI, coordinates, frames, directions, angles, donors, hashes, commands and earlier GIF previews.

Packaging validation on **2026-11-11**: both payloads rebuild byte-for-byte after
removing the optional runners. The cleaned package applies through real WARP with
the expected EPI identities and no skipped patches; the installed native
owner/trampoline protection fixture and QJS style/encoding checks pass. The
prerequisite, check-only, stale-payload and source-pin regressions also passed
before their runners were removed. No renderer, artwork or payload bytes changed.

Historical validation recorded before the 2026-11-11 packaging cleanup:

- Single-name removal: seven real-WARP cases cover the prior/current original
  name, reversed IDs/invocation, runtime INI, and missing-GRF/wrong-priority/
  missing-loader failures. Successful EXEs retain the pre-removal hashes and
  original `.epi` identity. The 602-case emitted-x86 owner suite and native
  owner/trampoline permissions pass unchanged. Source tests require the removed
  wrapper/catalog/export to be absent.
- Native equipment/resource regression: **602 cases**, with the exact same
  emitted owner x86 hash as the accepted baseline.
- The following larger artwork/geometry counts are historical (2026-09-07), not
  freshly rerun by this packaging/prerequisite revision:
- 668,160 execution cases and 1,182,240 original-resource draws across ten bodies.
- 77,952 accepted geometry cases with maximum change **0.0**.
- 75,792 added geometry draws and 602 equipment/resource ABI cases.
- All 96 required ACT/SPR pairs, including 60 packaged overlay entries.
- Actual WARP console application in both trees, matching binary EPI entry and three emitted hooks.

These are compiled-x86/native-projection tests, not exhaustive live GPU/occlusion acceptance. The installed working build was visually accepted; it was not replaced during source cleanup.

| Native hook | Original bytes |
|---|---|
| Equipment, 0x00D403A0 | 55 8B EC 6A FF |
| Final draw, 0x00C4A0D0 | 55 8B EC 83 EC 50 |
| Vertex depth, 0x00C4A647 | A1 F8 15 25 01 |

Injected addresses vary by patch order. The former metadata hook at 0x00605D41 and native ACT-frame call at 0x00D36EE4 remain stock in new builds.

On raw already-expanded PE inputs, the existing WARP section-header/raw-pointer
growth defect still needs the previously maintained scoped repair. This revision
does not fix the GUI serializer. The normal `.epi` recipe path should retain and
replay the selected loader with the dual-weapon patch.

| Runtime artifact | SHA-256 |
|---|---|
| compositor.dwcp | b8bf5902c798e4ba7a144d60f04f2b7dff3933414230e8cafc86cacb3bf33404 |
| legacy-support.dwls v2 | cbe42e80f62de5c64f1d5f6cd43740e2a60f41e67a1f69766a5d3f3edc8a2f81 |
| dual_weapon_male_assets.grf | 37a7e2aa876ab9b4383f86e00c0015a65555cebf919612ec2a4b57409c8930cc |

No server or character-record changes are included.
