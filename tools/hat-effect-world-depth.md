# HatEffect world depth — issue #77

Target: **2025-07-16 Ragexe**, original SHA-256
`ead7c0a316bc6c27705a5a6876daf5093abec31677f3c1af7525c1709b201bff`.

Issue: <https://github.com/CrazyBebop/WARP0716/issues/77>.

## Finding

The report describes an effect covering its wearer at distant zoom but being
cut by the wearer at close zoom. The issue's lists of effect IDs are predictions
from Lua draw-order flags, **not** a confirmed affected-ID matrix. The reporter
has not supplied the gender-change effect's ID.

The previous bridge reconstructed upper vertices along world Y using the
projection matrix. Ordinary native sprite rows do something different:
`0x00C4102B` uses `z + 0.16 * (screenY - anchorY)` before taking the reciprocal.
Consequently the two depth planes can cross. Increasing a fixed reciprocal-depth
bias cannot correct that discrepancy at every zoom.

The verifier exports the old QJS through real WARP, then executes the actual
bridge and native `0x00554040` with Unicorn. At camera distance 120 and row -96,
the historical effect Z is behind the native sprite-row plane. The receipt
records both values; this is a **numeric reproduction**, not a screenshot of
the reporter's particular effect or a reconstruction of their camera settings.

## Change

For HatEffect-scoped normalized Z only:

```text
row   = min(screenY - anchorY, 0)
depth = 1 / anchorRHW + nativeSpriteTilt * row
rhwZ  = (depth > 0 ? 1 / depth : anchorRHW) + contactBias
Z     = nativeDepthConversion(rhwZ)
```

The native tilt is read from `0x011DD478`, with its consuming instruction
verified before allocation/writes. The existing four-quantum contact bias
(`0x3827C5AC`) remains bounded. At/below the anchor the floor-safe plane remains
unchanged. Nonpositive/NaN denominators fall back to the anchor. NaN row input
uses SSE MINSS's zero operand.

The two original render call sites, scope wrapper, renderer submission, flags
and native draw-order routing are unchanged. This does **not** force every
HatEffect in front of its wearer or disable depth testing. Screen X/Y, texture
RHW (including its original layer bias), UV, colors, animation and lifecycle
remain native. Other screen STR users still execute the displaced instruction
and return to the stock continuation.

The old upper-vertex calculation also overwrote EAX/ECX and restored only the
low lanes of its temporary XMM registers. The smaller bridge needs no GPR
temporaries and saves/restores all 128 bits of XMM1/XMM4, including XMM1 around
the native conversion call. Its 151 bytes fit the existing 0x120-byte allocation.

## Reproduction and automated checks

Run from the repository root with the existing pefile/capstone/unicorn Python
environment and `win32/WARP_console.exe`:

```powershell
.\.venv-target-hud\Scripts\python.exe tools\verify_hat_effect_world_depth.py --baseline-ref 4be805c42664999c991f1e2c55a78f19b80f5108 --report tools\hat-effect-world-depth-evidence.json
```

`--source` and `--warp` override local binary locations. `--baseline-ref` reads
the original QJS bytes directly from Git into the temporary fixture. Alternatively,
`--baseline-qjs` accepts an unmodified patch file. Do not use PowerShell text
redirection to extract that CRLF/no-BOM file; preserve the raw `git show` bytes.
`--only` provides bounded test groups. Directory symlinks require Windows
Developer Mode or an elevated shell, as on the verified host.

Checks execute emitted machine code, not a JavaScript reimplementation:

- QJS source encoding/CRLF, banner alignment and indentation (also checked
  independently with the local `verify_qjs_patch_style.py` gate).
- Real QuickJS/WARP patch export, both HatEffect render-call wrappers and safe
  reapplication through WARP's own unpatch/reapply handling.
- Six camera distances, nine vertex rows, four native STR layer indices:
  **216 cases per export**, including full GPR/live-XMM preservation and exact
  stock RHW. Degenerate rows/denominators and unscoped STR paths are separate.
- Nearer/farther geometry depth comparisons, scoped native-code write coverage,
  complete bridge decode and native call/continuation targets.
- Eight individually corrupted native guards reject before activating hooks.
- Where available, both orders with `UniformSpriteRHW` and
  `FloorSafeSpriteDepth`; neither is a prerequisite of this patch.
- TemporaryDirectory teardown removes fixtures, read-only directory links and test clients
  on both success and Python exceptions. No deployed client/resources/settings
  are modified. Qt/data directories are linked, not duplicated. PE files are
  read from bytes (fast-load mode) to avoid Windows mmap file locks and expensive
  parsing of the client's unrelated imports/resources.

Compact results: [`hat-effect-world-depth-evidence.json`](hat-effect-world-depth-evidence.json).

## Acceptance boundary

Automated native execution verifies the calculation and ABI, **not** D3D
rasterization, interpolated overlap, all attachment offsets, or live visibility.
Do not carry the old July 14 visual acceptance claim forward to this revision.
The exact reported gender-change effect remains unavailable locally; the issue
also states that the maintainer's test setup could not render stock HatEffects.

Before marking this revision visually accepted, compare stock/old/fixed clients
with the reporter's effect and representative custom effects at near/far zoom
and low/high pitch. Check before/after-character flags, full-body clouds,
head-only effects, floor contact, partial opaque-wall clipping, wall contact,
animation, actor movement, map change, relog and teardown. Include overlapping
sprite/effect quads and attachment offsets rather than testing vertices alone.
Record effect IDs, client hashes and screenshots. The PR remains a draft until
that live matrix is supplied; no server/Lua resources are altered to mask it.