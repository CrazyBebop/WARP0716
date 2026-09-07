# Original dual/off-hand weapon sprites

For **2025-07-16 Ragexe 175220998**, this patch preserves original dagger, one-handed sword and axe artwork while dual wielding or using only an off-hand weapon.

## Required files

| File | Purpose |
|---|---|
| `Scripts/Patches/AllowDualCustomWeaponSprites.qjs` | Validates the client, owns resources, loads the bundles and installs three hooks |
| `Patches/Special.yml` | Registers the same exported patch name |
| `Inputs/DualWeaponRuntime/compositor.dwcp` | Compiled weapon compositor and placement data |
| `Inputs/DualWeaponRuntime/legacy-support.dwls` | Validated frozen support bundle; supplies the active depth helper |
| `Inputs/DualWeaponRuntime/dual_weapon_male_assets.grf` | Missing original-weapon resources for both genders |
| `Inputs/DualWeaponRuntime/embedded-grfs-20250716.ini` | Example archive list for the tested GRFsEmbedded installation |

**The QJS is not standalone.** It reads both binary bundles before writing hooks. Omitting either causes validation to fail. The compatibility GRF supplies missing job filenames; omitting it can restore generic fallback artwork for affected weapons.

Keep the directory structure when installing into WARP. Copy the GRF into the client directory and register it at highest priority in the loader the EXE actually uses. The example INI requires the named base archives to exist. With GRFsEmbedded, select the matching archive list when repatching; DATA.INI alone does not change the embedded list.

Apply to a source with stock dual-weapon hook bytes, preserving other patch selections through the WARP session. Occupied hooks are rejected.

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

The full generation tools, readable C source, authored profiles and machine evidence are retained in the [complete verified source snapshot](https://github.com/YlenXWalker/WARP0716/tree/f2a3a710f96fd8f1f705d8f7fd5ab19462a321a7). They are intentionally outside this PR's final runtime-only file diff.

The [detailed reference](https://github.com/YlenXWalker/WARP0716/blob/f2a3a710f96fd8f1f705d8f7fd5ab19462a321a7/docs/dual-wield-original-weapon-sprites.md) records the view list, native ABI, coordinates, frames, directions, angles, donors, hashes, commands and earlier GIF previews.

Verified results:

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

| Runtime artifact | SHA-256 |
|---|---|
| compositor.dwcp | b8bf5902c798e4ba7a144d60f04f2b7dff3933414230e8cafc86cacb3bf33404 |
| legacy-support.dwls | e6d0149196ef2a344f429b4ab4280c860d22a4bd20853514719372f00e8077d2 |
| dual_weapon_male_assets.grf | 37a7e2aa876ab9b4383f86e00c0015a65555cebf919612ec2a4b57409c8930cc |

No server or character-record changes are included.
