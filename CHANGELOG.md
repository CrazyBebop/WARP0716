# CrazyBebop - 2025-07-16 build (September 4, 2026)

> **Patch update - re-WARP to apply.** Two new patches, six fixes and a new `WARP.exe`. Re-apply WARP to use them.
>
> Easiest route: open **[WARPGATE](https://mirror2.romirrors.com/downloads/Warpgate.zip)**, use the **WARP** tab to update the patcher and this patch set, then re-apply your profile. Guides for the patches that need files from you are at **[warp.legacygamers.net/warp0716](https://warp.legacygamers.net/warp0716/)**.

## September 4 Update

### New patch: Party HP/SP Bars (Reforged) ([#34](https://github.com/CrazyBebop/WARP0716/issues/34))

Splits every party member's bar into an HP half and an SP half, in the party window and on the detached mini widgets, and draws the SP number beside it. You can set the HP and SP colours, with your own row separate from everyone else's so you are easy to find in a full party.

This one needs a change on your server as well: the client half alone gives you a split bar whose SP side never moves. The `SHOW_PARTY_SP` build flag makes rAthena send the 22-byte `0x0BAB` party packet carrying `sp` and `maxsp`, and adds the `@spbar` command so a player can hide their own SP from the party. The patch is in the repository at `examples/ShowPartySP/`, and the guide walks through applying it: **[Party HP/SP Bars guide](https://warp.legacygamers.net/warp0716/ShowPartySP/)**.

Party SP travels only to members who can see each other, which is the client's own behaviour for HP.

### New patch: Add your own buttons

Adds extra buttons to the row below the HP/SP bars in the Basic Info window, past the 25 the client ships with. Each one is written as `iconName = behaves like`: the icon name is also the file name, so the client loads `bt_<iconName>.bmp` and `bt_<iconName>_press.bmp` from `data\texture\<UI folder>\menu_icon\`, and `behaves like` names one of the stock buttons whose action the new one performs. Guide: **[Custom Buttons](https://warp.legacygamers.net/warp0716/CustomButtons/)**.

### Custom Jobs (Reforged): weapons and palettes ([#62](https://github.com/CrazyBebop/WARP0716/issues/62))

Reported by mimishi. A custom job's weapon hung in the air beside the character instead of sitting in its hand. Fixed, and the job's weapon sprite folders are now read from `PCHands.lua` at the moment you patch, so a new job needs a row there and nothing else.

The palette half was not a bug in the patch. `PCPals` is a filename **prefix**, while `PCPaths` and `PCHands` are **folder** names, so a folder named after your job means the client never finds the files. The **[Custom Jobs guide](https://warp.legacygamers.net/warp0716/CustomJobs/)** now names the exact folder, lists the files the client opens for your own value, and warns that a palette copied from another job keeps that job's prefix until you rename it.

### Hide Buttons / Show Buttons (New UI): every button, listed ([#24](https://github.com/CrazyBebop/WARP0716/issues/24))

Reported by gidzdlcrz. Both patches now list **every** button this client has, rather than only the ones the client leaves visible. On 2025-07-16 the three the client hides by itself are **Battleground, Booking and Twitter**, and they are selectable in both lists now; the prompt says which are already hidden, and picking one that is already in that state simply does nothing. Choosing the same button in both patches is rejected with an error naming it, rather than silently resolving one way.

### Fixed: EXP bar customization ([#49](https://github.com/CrazyBebop/WARP0716/issues/49))

The patched client would not start at all: a strange icon, then "This app can't run on your PC". It was writing over the executable's DOS header at offset 0, so Windows refused to load the image. Four stacked defects sat behind that one symptom and all four are fixed.

### Fixed: Resize Player HP/SP bar ([#52](https://github.com/CrazyBebop/WARP0716/issues/52))

It never appeared in WARP's patch list, because a build-date check hid it from a 2025-07-16 client. With that lifted it still only moved the bar, because the size it searched for is written differently on this client. Both fixed: the bar measures 120x20 in game, up from 60x9.

### Zoom: a 25% step, and a level you set yourself ([#50](https://github.com/CrazyBebop/WARP0716/issues/50))

**Increase Zoom Out (to 25%)** is the gentler step that was asked for, for when Max is too far out. **Increase Zoom Out (custom %)** takes the percentage you want over the client default and works out the distance, so `60` gives the camera 60% more range. **Max** was corrected as well: it used to pull back further than this client can draw, which showed black at the edges of the screen, and it now stops at the real limit.

All of them had been overwriting a constant the renderer also uses as its reference resolution, so they rescaled sprites and effects as well as moving the camera. They move the camera and nothing else now.

★ Remember to turn zoom out on in game with `/zoom`, or none of this shows: with the client's own setting off, the camera is capped tighter than stock.

### Walk Delay (Reforged) ([#39](https://github.com/CrazyBebop/WARP0716/issues/39))

Sets the delay between walk-click inputs in milliseconds. The old **Remove Walk Delay** patch was this one with the value pinned to zero, so it is retired. Do not go below 10: below that the character stops playing its walk animation.

### A new `win32/WARP.exe`

**Select Recommended** now loads `profiles/community_recommended.yml`, which is 37 patches that give you a working English client in one click, without answering a single question. The dead **Convert Profile to Session** row is gone from the menu.

### Housekeeping

- **Retired**, declarations commented out with the reason, implementations left intact so re-enabling is uncommenting one block: `NoWalkDelay` (merged into Walk Delay), `CancelToLogin` (unsatisfiable on this client and redundant), `MsgStrings` and `QuestDisplay` (the client reads those files anyway). `SendClientFlags` is no longer recommended.
- **`docs/` has left the repository.** The guides live on **[warp.legacygamers.net](https://warp.legacygamers.net/warp0716/)**, where they are rebuilt with the patch set. What used to sit under `docs/` and is not a guide has moved to **`examples/`**: the Custom Jobs example job and its annotated Lua reference, and the Party HP/SP Bars server patch.
- `profiles/community_recommended.yml` rebuilt against the current patch set.

---

# CrazyBebop - 2025-07-16 build (August 18, 2026)

> **Patch update - re-WARP to apply.** Seven new patches and a Simplified Chinese translation. Re-apply WARP to use them.

## August 18 Update

### New patch: Tighter Entity Click Area ([#63](https://github.com/CrazyBebop/WARP0716/pull/63))

The client does not let an entity's clickable box get small. It widens every one up to a minimum worked out from your window width, `width / 640 x 40` pixels for actors and `x 34` for map NPCs and skill units. At 1600x900 that is a 100 px box around a sprite that may be a fraction of it, so a poring standing near an NPC can swallow clicks meant for the NPC. This patch lets you shrink that floor, so small things claim only the space they occupy. Thanks to Stingor.

### New patch: Restore the "View Skill Info." checkbox ([#61](https://github.com/CrazyBebop/WARP0716/pull/61))

Older Ragexe builds had a checkbox in the top right of the ALT+S Skill Tree, and while it was ticked, hovering a skill popped its detail window next to the cursor instead of making you right-click. The client still owns the option internally and still saves it; only the checkbox went missing. This brings it back. Thanks to Stingor.

### New patch: Restore GM weapon trails ([#60](https://github.com/CrazyBebop/WARP0716/pull/60))

Accounts listed under `<admin>` in your clientinfo lose the weapon trail, the blade gleam drawn while attacking. The client writes 0 into that sprite layer for GM accounts, so the renderer drops it. **Disable GM sprite** does not cover this, because it only touches the two name-list functions. Thanks to Stingor.

### New patch: Restore Sonic Blow and Arrow Vulcan animations ([#58](https://github.com/CrazyBebop/WARP0716/pull/58))

Gives Sonic Blow and Arrow Vulcan back the attacker's sprite animation. Pick either or both when you apply it. Gravity never deleted the animations, only the routing that chose them: the client still plays it for Chain Crush Combo, and this sends the selected skills back down that same path. Sound and effects were never affected. Thanks to Stingor.

### New patch: Mark pet chatter in chat ([#55](https://github.com/CrazyBebop/WARP0716/pull/55))

Pet chatter arrives with no sender and the ordinary message type, so a pet named after a player reads exactly like that player talking. This tags every automated pet line with a marker of your choosing, default `pet`, with a choice of brackets. Thanks to Stingor.

### New patch: No bogus "not your guildsman" whisper warning ([#54](https://github.com/CrazyBebop/WARP0716/pull/54))

Stops the "This character is not your guildsman" and "This name is not registered in your Friend List" lines the client prints on incoming whispers. They exist to flag impostors who swap a capital I for a lowercase l, which is a real problem, but the comparison is far too loose and fires on ordinary names that merely resemble a friend's. Thanks to Stingor.

### New patch: Shared head palettes for Doram ([#53](https://github.com/CrazyBebop/WARP0716/pull/53))

The existing shared head palette patches skip the Doram races entirely, so a Doram still needs one palette file per hairstyle **and** per gender while everyone else needs one. This applies the same shared naming to Doram. The files stay in the Doram race folder on purpose: Doram sprites do not share the human palette indexing, and pointing them at the human files leaves the character mostly black. Thanks to Stingor.

### Simplified Chinese translation ([#56](https://github.com/CrazyBebop/WARP0716/pull/56))

WARP's own interface is now available in Simplified Chinese. Thanks to jj163494, building on xvn5002036's Traditional Chinese work.

---

# CrazyBebop - 2025-07-16 build (July 29, 2026)

> **EXE update - grab the new Ragexe.** These fixes live in the injected EXE itself, not in a WARP patch, so re-WARPing the exe you already have will **not** pick them up.
>
> Get it through **[WARPGATE](https://mirror2.romirrors.com/downloads/Warpgate.zip)**: unzip, run it, and use the **RAGEXE** tab. Then re-apply your patch set if you use one.
>
> If you have already patched your own executable, WARPGATE keeps yours and will not overwrite it. Choose ours from the RAGEXE tab (your copy is saved as a `.bak`), or re-patch starting from the new one.

## July 29 Update

### The "exit" button on server select now actually exits ([#17](https://github.com/CrazyBebop/WARP0716/issues/17))

Reported by gidzdlcrz: on the service/server select screen, pressing the second button made the window vanish and left you with nothing on screen. The only way out was to close the client.

The button was renamed to "exit" in an earlier build, but only the label changed. It still performed a cancel, and cancel on that screen closes the window and then sends a message the client ignores while it is on the server list, so nothing replaces it.

It now uses the client's own exit path, which was already present and simply never shown: a confirmation dialog, and a clean shutdown if you accept. Pressing cancel on that dialog returns you to the server list with everything intact.

### Multi-connection clientinfo.xml: switching servers mid-session now works

If your `clientinfo.xml` lists more than one `<connection>`, players can pick a server on the service select screen. That worked from a fresh start, but not after you had already played: log in to one server, go all the way in-game, back out to the server list, pick a **different** server, and the client would fail to connect.

The old code kept its own private copy of every server's address and port and looked yours up by position in that list. That copy went stale once you had been in-game, and it could also drift out of step with the on-screen list if any `<connection>` was missing an `<address>`. It was capped at 8 servers, silently.

It now reads the address and port the client itself resolved for the connection you picked, so there is nothing of ours to go stale, no cap, and no way for the list positions to disagree. Verified against two live servers: pick the second or third entry after a full in-game session and you land on the right one.

### Leaner startup, and the 8 server limit is gone

The old code scanned your entire `clientinfo.xml` at startup and built its own private copy of every server's address and port before the login screen even appeared. That work scaled with the length of your server list, and it was capped at 8 servers.

None of that happens now. The client reads the address and port for the server you picked, at the moment it connects. Startup does strictly less work, there is no cap on how many servers you can list, and there is no second copy of your server list to fall out of step with the file.

### clientinfo.xml problems now tell you what is wrong

Previously a missing, unreadable or incomplete `clientinfo.xml` just produced a failed connection with no explanation. The client now names the actual problem: the file could not be opened, or it has no usable `<clientinfo>`/`<connection>`, or the server you picked has no `<address>`.

---

# CrazyBebop - 2025-07-16 build (July 20, 2026)

> **Patch update - re-WARP to apply.** Adds one new patch for Skill Tree performance; re-apply WARP to use it.

## July 20 Update

### New patch: Reduce expensive UI rendering ([#45](https://github.com/CrazyBebop/WARP0716/pull/45))

The ALT+S Skill Tree rebuilds its entire icon grid every single frame, even when nothing on it has changed. This patch skips that rebuild unless something actually changed: tab, hover, scroll, skill points, window size, or the client's own dirty flag.

Measured on a test client with the Skill Tree open, comparing both states on one running process: the stock client repainted on every frame and sat around 90% CPU, while the gated version repainted **zero times across 256 consecutive idle frames** and dropped under 1%.

Thanks to YlenXWalker and Stingor.

**Idle repaint interval.** The repaint being skipped is also what draws the character preview in the corner of the window, and that preview's animation is driven by a timer. Skipping every frame therefore leaves it frozen while the window sits idle. When you apply the patch it now asks for a minimum repaint interval:

- **Off** - cheapest, the preview stops animating while idle
- **200 / 400 / 600 / 800 ms** - preview keeps animating

Default is 600 ms. The preview sprite only advances about every 600 ms, so repainting faster than that redraws the same frame for no benefit, and longer intervals cost less.

---

# CrazyBebop - 2025-07-16 build (July 15, 2026)

> **Patch update - re-WARP to apply.** This adds four community patches and fixes the mob/boss bar resize crash; re-apply WARP with the updated patches to use them.

## July 15 Update

### Resize Mob & Boss Bars no longer crash ([#22](https://github.com/CrazyBebop/WARP0716/issues/22))

The **ResizeNormalBar**, **ResizeMiniBossBar**, and **ResizeBossBar** patches now work on the 2025-07-16 client. This was actually two separate bugs stacked on top of each other:

1. **Patcher crash when enabling more than one.** Each Resize\*Bar patch reopened the shared `MobHP` code tag, so applying a second one re-ran the tag setup and crashed the WARP patcher (access violation, `0xC0000005`). Fixed with a guard: the shared hook is built once and each bar only writes its own width/height.

2. **Client crash on mob-bar render.** The patcher crash was hiding a second problem. WARP's automatic mob-bar hook detection mis-reads the 07-16 client and builds a malformed hook, which crashed the *client* the moment a monster HP bar was drawn (for example, clicking a mob). The hook location itself was correct; only the auto-generated code was wrong. Replaced with a hardcoded, verified 07-16 hook that reads the monster type from the correct field.

Confirmed in-game: Boss, Mini-boss, and Normal bars each render at their configured size with no crash.

Thanks to Gardosen for reporting it, and to themidgargospel for the extra detail in the thread.

### New patch: HatEffect world-depth occlusion ([#43](https://github.com/CrazyBebop/WARP0716/pull/43))

Makes hat effects behave like special effects: they are now correctly occluded by buildings, walls, and other world geometry instead of drawing on top of everything. Thanks to YlenXWalker.

### New patch: Dual weapon and off-hand sprites ([#42](https://github.com/CrazyBebop/WARP0716/pull/42))

Adds an option to render dual-wield and off-hand weapons with their original weapon sprites. Thanks to YlenXWalker.

### New patch: Custom client codepage ([#37](https://github.com/CrazyBebop/WARP0716/pull/37))

A QJS-only patch that forces the client's text codepage, so text renders correctly regardless of the OS locale. Thanks to YlenXWalker.

### Chat background patches split, plus Bigger Inventory ([#35](https://github.com/CrazyBebop/WARP0716/pull/35))

The main chat-background patch was split out and detached/whisper chat-background patches were added, which also fixes a red/blue color swap in the old opacity patch (the color value was being read as BGR). Also adds a **BiggerInventoryWindow** patch. Thanks to Stingor.

---

# CrazyBebop — 2025-07-16 build (May 15, 2026)

> **Binary patch — re-WARP required.** Unlike the May 6 / Apr 21 hotfixes, this one changes the `CustomJobs` patch itself, not just Lua data. You must re-apply the WARP patch with the updated `CustomJobs.qjs` for it to take effect — dropping new Lua files alone will **not** enable it.

## May 15 Update

### Custom jobs can now use the Doram race

Custom jobs intended to render as Doram (e.g. a job pointing `PCPaths` at `"summoner"`) were always drawn with the **Human** body — Doram body sprites loaded human heads, offsets, scale, and nameplate positions were wrong. ([GitHub #27](https://github.com/CrazyBebop/WARP0716/issues/27))

Cause: the client decides Human vs Doram by calling an internal `is_doram_job_id` check that is hardcoded to the **stock Summoner / Mystic Summoner IDs only**. Custom job IDs are never in that set, so they always took the Human sprite path — and the same check gates ~40 other behaviors (item offsets, sprite scale, shadow position, nameplate Y-offset, the item layer renderer, character select/create, the styling shop, skill-effect positioning).

Fixed with a new **`CustomJobs` Phase 13** patch that hooks the tail of that check and consults a Lua table, `PCRace`. Set an entry and the job follows the Doram code paths the stock Summoner uses. Define it in any JobInfo Lua file (e.g. `PCIds.lua` or a new `PCRace.lua`):

```
PCRace = PCRace or {}
PCRace[PCIds.MY_DORAM_NOVICE] = "doram"
```

Any non-nil value enables it; `"doram"` reads well and reserves room for future race values. Stock Summoner / Mystic Summoner are unaffected — the original check still runs first and short-circuits for them, so there is zero behavior change for non-custom jobs.

Doram custom-job body sprites go in the Doram folder, not the Human one: `data/sprite/도람족/몸통/…` (CP949 `µµ¶÷Á·\¸öÅë\…`) instead of `인간족/몸통/`. Everything else (`.act`, `costume_1/`, IMF, palette, icon) follows the same rules as a normal custom job.

Thanks to pepeuprog for reporting it.

### Custom Jobs guide — new "Doram Race" section
[Online guide](https://legacygamers.net/docs/public/customjobs-reforged/) gained a **Doram Race** subsection under Step 2 documenting the `PCRace` API and the Doram sprite paths.

### To install
Re-apply the WARP patch using the updated `CustomJobs.qjs` from this repo, then add your `PCRace` entries to a JobInfo Lua file. Because this is a binary change, the Lua-only install path used by the May 6 / Apr 21 hotfixes does **not** apply here — you must re-WARP.

---

# CrazyBebop — 2025-07-16 build (May 6, 2026)

> **Lua-only — no re-WARP needed.** Drop the new `PCFuncs.lua` and `PCIds.lua` (and optionally `PCNames.lua`) into `data/luafiles514/lua files/JobInfo/`, overwriting existing. Lua data files are loaded at runtime, not baked into the exe.

## May 6 Hotfix

### Mounted classes — Job name no longer shows "Poring"
Players on a peco / dragon / mado / wolf / gryphon mount were seeing **"Poring"** as their class in the BasicInfo window, character select, and party UI — Lord Knight, Paladin, Rune Knight, Royal Guard, Mechanic, Ranger, Dragon Knight, and other 4th-class jobs all affected.

Cause: the stock client uses *2 mounted variant IDs (e.g. `LORD_KNIGHT 4008` → `LORD_KNIGHT2 4014`) for the actor's effective class while mounted, and the GRF-loaded job name table only populates the **base** IDs. When the client looked up `PCNames[4014]`, the entry was missing and the lookup fell through to a hardcoded "Poring" fallback.

Fixed by adding a second auto-populate pass in `PCFuncs.lua` that copies each base class name onto its mounted variant(s). The mapping was extracted from the client's mounted-job lookup function (`CMode::GetJobClassID` at 0x00d5b580) — covers all stock peco mounts, Rune Knight's five dragon colors, Mechanic's mado gear, Royal Guard's gryphon, Ranger's wolf, and the 4th-class mount IDs. User overrides in `PCNames` still win — the pass only fills entries that are currently nil.

### Stock job constants now usable as `PCIds.NAME`
Previously, only your custom job IDs were defined in `PCIds.lua` — stock constants like `PCIds.LORD_KNIGHT2`, `PCIds.PALADIN2`, `PCIds.WARLOCK`, etc. evaluated to `nil`. Writing `PCNames[PCIds.LORD_KNIGHT2] = "Holy Knight"` was a silent no-op; you had to use the raw numeric ID (`PCNames[4014] = "Holy Knight"`) instead.

The shipped `PCIds.lua` now includes a `do…end` block at the top that pre-defines ~170 stock constants (NOVICE through 4th-class jobs and their mounts) before your custom IDs are added. After this, both forms work:

```
PCNames[PCIds.LORD_KNIGHT2] = "Holy Knight"   -- by name
PCNames[4014]               = "Holy Knight"   -- by raw ID (same thing)
```

Aliases are included for both rAthena naming (`LORD_KNIGHT2`, `RUNE_KNIGHT_T`) and legacy WARP naming (`LORD_MOUNT`, `RUNE_KNIGHT_H`) — pick whichever convention you prefer. Add your custom IDs after the **ADD CUSTOM JOBS BELOW** marker line.

The previous comment "Stock job IDs are loaded from GRF" was a misconception — the GRF only loads stock *names* (via `PCJobNameTable`), not the Lua-side constant table. Header comments updated to match reality.

### `JOB_SKILL_TIER` now actually applies to custom job chains
Multi-tier custom job chains (Base → 2nd → 3rd) declared via `JOB_SKILL_TIER` in `PCIds.lua` were silently collapsing onto a single skill-tree tab. The `InitSkillTreeView` wrapper that reads `JOB_SKILL_TIER` at runtime had been missing from the WARP `Inputs/` source — never committed back from a deployed environment. Now included in `PCFuncs.lua` as the canonical source.

### PCNames.lua header refreshed (optional)
The shipped `PCNames.lua` header now shows both `PCNames[PCIds.X]` and `PCNames[4014]` examples for renaming stock jobs. Cosmetic only — your existing `PCNames.lua` keeps working as-is. Skip this file unless you want the updated examples.

### Custom Jobs guide — significant additions
[Online guide](https://legacygamers.net/docs/public/customjobs-reforged/) updated with new sections:
- **Stock PCIds auto-populate** callout under PCIds.lua, plus PCNames examples now show both `PCIds.X` and raw-ID forms side-by-side
- **Gender-specific names** — `PCNames_M` / `PCNames_F` for male/female overrides (the stock Bard/Dancer convention)
- **Multi-language names** — `LT_<N>` per-language sub-tables; works on every lookup table, not just PCNames
- **Inheritance Tables** — `PCNameInheritTbl` / `PCPathInheritTbl` / etc. for tier-style fallback chains, with the matching `MapPC*` resolver functions
- **`JT_` vs `JOB_`** naming-convention callout (skillinfoz `JOBID.JT_NAME` vs server-side `JOB_NAME`)
- **Mount Support** rewritten — stock mounts work automatically (no PCIds setup needed), custom mount riding IDs need their own entries across all five lookup tables (PCPaths / PCNames / PCPals / PCHands / PCImfs)
- Step 1 warning expanded to mention the Phase 5 4345 floor and the `convert_job_to_trans_or_baby` sprite-mangling path

### To install
Replace `data/luafiles514/lua files/JobInfo/PCFuncs.lua` and `PCIds.lua` (and optionally `PCNames.lua`) in your client's data folder with the new copies. No re-WARP, no exe changes — Lua files are runtime-loaded.

---

# CrazyBebop — 2025-07-16 build (Apr 21, 2026)

## Apr 21 Update

### Rune System Paths — Arbitrary Length Within Slot Capacity
The upstream rune-path patches enforced an exact byte-length match against the original `System\Rune\…` defaults. That made it impossible to use paths like `SystemEN\Rune\itemDecom.lub` (27 chars where the original is 25), which is needed for consistency with Chris's ROenglishRE translation layout.

The 07-16 client loads each rune file via an inlined MOVUPS+MOVQ+MOV(byte|dword) copy sequence with a hardcoded byte count, a hardcoded `std::string::size_` immediate, and a hardcoded null-terminator offset — all set to the original path's length. The strict check existed to stop replacements that would truncate (too long) or read past the end (too short).

Our fork extends the patch logic to handle all three cases without changing the injection:

- **Shorter replacements** — allocate a fresh buffer, write the new path, null-pad out to the original length, then point the MOV source operands at the padded buffer. The client still copies the full original byte count, but the C-string terminates at the first null so file loading picks up the shorter path correctly. `std::string::size_` stays at the original length — harmless for file APIs that use `c_str()`.
- **Longer replacements on byte-copy sites** (`itemDecom`, `rune_info`) — flip `MOV byte → MOV dword` at the two opcode bytes (`0x8A → 0x8B` and `0x88 → 0x89`, both same instruction size so no shifting), then bump the length immediate and null-terminator offset to the new length. Extends the copy chain from 25 to up to 28 bytes, supporting original+1 through original+3.
- **runesystemid** already uses `MOV dword` in stock; capped at the original length.
- **runeSystem_table** uses two `MOVUPS` copying a fixed 32 bytes; capped at the original length.

Verified same instruction offsets on both 07-16 and 06-04 — the VC compiler produces identical sequences.

### CustomClientInfo — Works on 07-16 (Injected Pipeline)
The stock `CustomClientInfo` patch searched for the `clientinfo.xml` literal as a single string. The 07-16 client doesn't store it that way — the injected clientinfo loader composes the filename on the stack at runtime via four `MOV [ESP+N], imm32` instructions. Result: the patch was always hidden on injected exes.

Added a detection path that recognizes the 4-MOV signature (`C7 04 24 63 6C 69 65 C7 44 24 04 6E 74 69 6E C7 44 24 08 66 6F 2E 78 C7 44 24 0C 6D 6C 00 00`). When found, the patch prompts for a new filename (≤15 chars — the on-stack buffer is 16 bytes including the null terminator) and rewrites the four dword immediates in place. The validator accepts either the injected layout OR a stock `ClInfoAddr > 0`.

To test: select `Customize ClientInfo file` in the WARP UI, type a new name (e.g. `lgro.xml`), drop your renamed XML at `<client>\data\<newname>.xml`.

### Translations EN — Rune Tablet Label
Added the "Rune of %s" TranslateClient entry (Korean bytes `25 73 C0 C7 20 B7 E9 20 C1 B6 B0 A2` → `Rune of %s`). Used by the Rune Tablet encyclopedia entries (e.g. "Rune of Night Market Bebe").

---

# CrazyBebop — 2025-07-16 build (Mar 29, 2026)

## Mar 29 Update

### Allow 65k Hair Styles — Fixed
Fixed a bug where the first ~12 hair styles displayed the wrong sprite when `Allow65kHairs` was enabled. The 07-16 client has a remapped hair name table internally, and the original patch bypassed it. The fix preserves the table for standard styles and uses dynamic number conversion for custom styles beyond 42.

- Works correctly on the character creation screen, character select, and in-game
- Works independently of Custom Jobs, and both can be enabled together
- Includes an open-source mid-headgear hook replacing the old encrypted one
- `IncreaseHairsLimit` has been removed (superseded)

### PreviewInTrader — Cashshop Crash Fix ([#20](https://github.com/CrazyBebop/WARP0716/issues/20))
Opening an old-style `cashshop` NPC caused an instant crash when `PreviewInTrader` was enabled. The patch tried to access a window object that doesn't exist for cashshop windows. Fixed with a null pointer check.

## Mar 26 Update

### InsensitiveStorageSearch — Fixed ([#16](https://github.com/CrazyBebop/WARP0716/issues/16))
Case-insensitive storage search wasn't working on the 07-16 client. The patch was matching the wrong function internally. Fixed with an updated pattern for the 07-16 compiler.

### Custom Jobs — Ground Skill Crash Fix
Using ground-based skills (like Storm Gust) on mobs caused a crash when Custom Jobs was enabled. Fixed — the sprite name lookup now uses a safer code path with validation. All standard and custom jobs work correctly.

### Cancel-Exit on Service Select
The server select screen is now fully functional. Previously the cancel button did nothing — now it shows a "Are you sure you want to quit?" dialog and exits the client. The cancel button also automatically changes to say "exit" when on this screen. No extra files needed — the exit button graphics already exist in the GRF.

### Multi-Connection clientinfo.xml — Fixed
Servers with multiple entries in `clientinfo.xml` now work correctly. Previously all connections went to the first entry's IP regardless of which server the player selected. Now each server entry's address and port are stored separately, and the client connects to the right one based on the player's selection.

Combined with the cancel-exit fix above, you can now list multiple servers and players will see the server select screen, pick their server, and connect to the correct one.

### DisableEquipAttrButton — Fixed ([#12](https://github.com/CrazyBebop/WARP0716/issues/12))
Hides the equipment attribute button in the equipment window. The original patch didn't work on the 07-16 client. Fixed by NOPing the AddChild call that adds the button.

### Removed Patches
The following patches have been removed — they don't apply to the 07-16 client:

- **TranslateTaekwon** — Not needed, `TranslateClient` + Lua handles translations instead
- **IncreaseHairsLimit** — Replaced by Allow65kHairs
- **NoSerialDisplay** — Not compatible with the 07-16 client
- **SelectLoginBG** — Not compatible with the 07-16 client
- **RestoreAutoFollow** — Only applies to Zero clients

---

## Mar 19 Update

### Enable Official Custom Fonts (Reforged) — Full Rewrite
The original `EnableEotFonts` patch didn't work on modern Windows because Microsoft removed support for the embedded font format (`.eot`) that the RO client uses. The patch appeared to apply but fonts never actually loaded.

This rewrite takes a completely different approach — it loads `.ttf` fonts directly through the standard Windows font API, the same way the client already loads its SCDream fonts.

- **How it works** — When the client starts up, the patch loads all `.ttf` files from `System\Font\` before any UI renders. It also fixes the font name references in the binary so `CreateFont` calls match the `.ttf` filenames
- **Font file management** — On apply, WARP prompts for your client folder, copies the included `.ttf` fonts to `System\Font\`, and optionally deletes the old `.eot` files
- **Custom fonts** — You can replace any `.ttf` in `System\Font\` with your own font (same filename). `@font 1-9` uses whatever `.ttf` is there — it's client-side only, no one else sees your fonts
- **FixFontsCharset** — Auto-enables `FixFontsCharset` which had a crash bug in the original version (now fixed)

Pre-converted `.ttf` files for all 13 fonts are included in `Inputs/Fonts/`.

**Renamed:** `EnableEotFonts` → `EnableCustomFonts`

### FixFontsCharset — Crash Fix
The original version of this patch had a bug that corrupted an internal pointer, causing random crashes when rendering text. Fixed by using a different register for the charset lookup.

## Mar 18 Update

### Custom Jobs (Reforged) — Major Update

The Custom Jobs patch has been significantly expanded — all built from scratch for the 07-16 client. This update adds baby class support, multi-tier skill trees, mount integration, and much more.

**What's new for server owners:**
- **Baby class support** — Baby variants of custom jobs now render at 75% size, just like official baby classes. Add your baby job IDs to `Shrink_Map` in PCIds.lua
- **Multi-tier skill trees** — Create job chains like Novice → 2nd Class → 3rd Class with proper tab merging. The first tab automatically combines Novice + base class skills (same behavior as Night Watch). Configure tiers in PCIds.lua via `JOB_SKILL_TIER`
- **Mount support** — Custom jobs can use the Boarding Halter (item 12622). Define mount sprite IDs in `PCMounts` and `Halter_Table` in PCIds.lua
- **Minimal Lua files** — Your Lua files only need custom job entries. Stock job data loads automatically from the GRF. All files use `Table = Table or {}` guards for safe additive loading
- **Error display** — When Lua files fail to load, you now get clear error messages. Choose between Silent, Log File, or Popup mode via the WARP patch options
- **Working example** — The `example/` folder and WARP Inputs include a complete EXAMPLE_JOB (ID 4435) with a baby variant (ID 4436), ready to copy into your client

**Technical details:**
- All Lua lookups use direct Lua C API calls at runtime, bypassing a broken internal function in the 07-16 client
- Palette and head sprite tables expanded to support up to 10,000 custom job classes
- Costume_1 sprite files are required for custom jobs (client crashes without them after ~1 minute)
- Patch renamed to "Enable Custom Jobs (Reforged)"

**Guide:** See the [Custom Jobs Guide](docs/CustomJobs/CUSTOM_JOBS_GUIDE.html) or [online version](https://legacygamers.net/docs/public/customjobs-reforged/) for full setup instructions with examples.

### IncreaseHairsLimit (64K Hair Patch) — Compatibility Fix
- The hair limit patch now works alongside Custom Jobs without crashing
- Previously both patches conflicted with each other, causing a crash on startup
- **Note:** This patch was later replaced by `Allow65kHairs` in the Mar 26 update

## Mar 13 Update

### Custom Jobs — Initial Release
- Full rewrite of the Custom Jobs patch for the 07-16 client
- Job names, sprite paths, palettes, head sprites, and display names all driven by Lua files
- Supports up to 10,000 custom job classes
- Custom job sprites render correctly in character select, creation, and in-game
- Example sprite, IMF, and icon files included in `examples/CustomJobs/data/`

### New Dark Theme — WARP0716
- New icons, recommend stamps, and editor font
- Original themes available as "Classic" and "Classic_Dark" in the style dropdown

## Mar 12 Update

### RagHash.dat Crash Fix
- Stale or leftover `RagHash.dat` in the client folder no longer crashes the client
- The NoGGuard patch now handles this automatically — no more need to manually delete the file

### GRFsFromIni Crash Fix
- Invalid or nonexistent GRF entries in `DATA.INI` no longer crash the client
- The patch now checks if each GRF file exists before trying to load it

## Mar 11 Update

### CustomIcon — Fixed
- Custom icons now work with any size and bit depth, including 256x256 PNG icons
- The original version only accepted tiny 32x32 icons
- All icon display contexts (Explorer, taskbar, window title) show the custom icon

## Mar 10 Update

### CustomJobs — Complete for 07-16
- All job tables now driven by Lua files (`PCIds`, `PCPaths`, `PCImfs`, `PCHands`, `PCPals`, `PCNames`, `PCFuncs`) — add custom jobs without any additional binary patching

### Dead Code Cleanup
- Removed unused code and 20 dead patch definitions that weren't applicable to 07-16

### Upstream Merge (hiphop9/Warp2025)
- Merged 5 commits from Mar 7–10

### Patch Descriptions Rewritten
- All patch YAML files rewritten with clear, user-friendly descriptions
- Every patch now explains what it does, why you'd want it, and any requirements or conflicts

### Known Conflict: NoPassEncr vs UseSSOLogin
- Don't enable both `UseSSOLogin` and `NoPassEncr` in the same profile — they conflict. The WARP GUI handles this automatically, but if you're using YAML profiles, only list one or the other

---

# CrazyBebop — 2025-07-16 build (Mar 9, 2026)

## Patch Fixes (15 total, 0 errors remaining)
15 patches were fixed to work with the 07-16 client's compiler differences (VS2022/VC14.29). Each patch had byte patterns or memory offsets that didn't match the 07-16 binary:

- **CallKoreaClientInfo**, **NoEarthQuake**, **NoEquipWinTitle**, **CustomShields**, **CustomCharCreateId**, **IgnoreEntryQueueErr**, **MoveUpItemCount**, **CustomFriendsLimit**, **AllowSkillSpam**, **CustomMissingLauncherMsg**, **LowCamAngle / MediumCamAngle / HighCamAngle**, **HideBuildInfo**

## Removed Patches (already baked into the EXE)
- **NoLoginOTP** — OTP login flow is already patched in the EXE before WARP
- **EnableDnsSupport** — Server addressing via clientinfo.xml is already handled in the EXE
- **HidePacketsFromPEEK** — 07-16 natively handles this, no patch needed

## Removed Patches (not applicable to 07-16)
- **NoFilenameCheck** — Gravity removed the filename check entirely in 07-16
- **CustomFriendsLimit** — The friends list UI was redesigned in 07-16, nothing to patch
- **NoGNJoyLaunch** — GNJoy launch URLs are already zeroed in the EXE

## Patches that auto-skip on 07-16
- **CustomJobs** — FIXED in later updates (see above)
- **CustomSlotHLColor** — Not fixable. 07-16 uses a different system for slot highlight colors

## Verified Working
All of the following patches have been tested and confirmed working on the 2025-07-16 client:

NoWavyScreen, EnableWho, EnableShowName, MediumCamAngle, UseOldLogin, UseSSOLogin, AlwaysAscii, CallKoreaClientInfo, PlainTextDesc, LoadKrExtSettings, HideBuildInfo, FixArrowsCharset, TranslateClient, NoGGuard, MsgStrings, QuestDisplay, CustomItemInfoLub, CustomAchieveLub, CustomTownInfoLub, CustomTipboxLub, CustomMapInfoLub, CustomOngQuestInfoLub, CustomRcmdQuestInfoLub, CustomspopupLub, CustomQuestQualiLub, IncrMapQuality, DataFolderFirst, GRFsFromIni, EnableSysMenu, No1and1Arg, RestoreIcon, NoNagle, SendClientFlags, NoLoginEncr, OpenToServiceSelect, GuildBrackets, FixChatAt, NoHourly, NoHelpMsg, FixSkillbarReset, NoGravityAds, NoGravityLogo, FixLatestNCWin, DisConnToLogin, CustomInventoryLimit, CustomInventoryExpandingLimit, NoCharnameLimit, NoUsernameLimit, NoPasswordLimit, NoEquipWinTitle, NoEarthQuake, CustomEncKeys, Zoom (25%/50%/75%/Max)

## User-Friendly Improvements
- **This build of WARP only accepts the 2025-07-16 client EXE**
- **Title bar** changed to "WARP for 2025-07-16" so it's clear which client this targets
- **"Loaded Date" label** renamed to "Client Date" for clarity
- **Patch descriptions rewritten** — Tooltips now explain what each patch actually does in plain language
- **Recommend flags reviewed** — Commonly needed patches are marked as recommended so new users get a good default set
- **CustomPath.qjs** — When selecting a Custom*Lub patch, the input now defaults to the original path but shows the recommended `SystemEN/` path for llchrisll Translation Project users
- **Translations_EN.yml** cleaned from 157 to 16 working entries
- **AddLuaOverrides** link updated to llchrisll's current documentation URL



# Skylove — 2025-06-04 build
- ShowReplayBtn
- @llchrisll: spopup & QuestQualificationInfo patches; added Rune System Lua and fixed related issues
- NPC Dialogue Scrolling
- Preview in Shop
- Chat Repeat
- Data Folder First
- No Hourly
- Increase Zoom
- Enable Proxy
- Load KrExtSettings
- License Screen Visibility
- Enable Flag Animation
- Ignore Palette errors
- Increase Human/Doram Hair Limit
- IgnoreLuaErr
- Enable Emblem hover for BG
- HideNewwButtons
- ShowNewButtons
- RestoreBattlegroundUI
- DisableTraitStatusButton
- HideTraitStatusButton
- Hide itemba
- PreviewInTrader
- Remove Eq Window Title
- IncreaseHairsLimit
- RestoreCpsDll
- CustomQSDelay
- Allow all items in Shortcut
- CustomInventoryExpandingLimit
- CustomInventoryLimit 
- AllowAPBarforAllJobs
- HideCashShop
- ResizeNpcBox
- DisableDoram
- HideProbabilityUI
- FixFontsCharset
- AllowHomunSkills
- EnablePingLog
- RemoveMaxNumbersLimit
- FixSelectMenuReset
- FixSelectMenuWidthExpansion
- ChangeGoldPCMaxPoints
- FixSkillbarReset
- AllianceChatHotkeySelector


# 2024-08-07 Changes

## Common Updates
- Updated Copyright year in all the Init & Support files.

## Patch Updates
- Fixed Init modules to work with latest clients (i.e. 2024).
- Some amount of validation is still needed for some of them especially LUA which will be done while fixing the patches.


# 2023-08-27 Changes

## Common Updates
- Updated Copyright year in all the files.

## Script Updates
- Updated **`$$`** function to accept 3 arguments to show as `arg1 : arg2 - arg3`.

  Also fixed angled brackets not being displayed in console.


# 2022-12-30 Changes

## Patch Updates
- Fixed bug in [Enforce 0 C in Cash Shop](https://github.com/Neo-Mind/WARP/issues/115) patch.

- Updated valid build dates for [Fix Homunculi AI](https://github.com/Neo-Mind/WARP/issues/93) patch.

- Fixed bug in [Increase Headgear View ID](https://discord.com/channels/780647066871136266/1051858994584633404) patch.


# 2022-10-05 Changes

## Patch Updates
- Updated Restore App Icon & Customize App icon patches.

	- Restore enables the new bigger icon in latest clients.
	
	- Custom icon has no limits now aside from anything Windows imposes.

## Extension Updates
- Fixed **`DumpImportTable`** extension for certain clients where LUT address is set as 0.

## Script Updates
- Updated **`RsrcEntry`** class with better traverse function & a dump function to report the hierarchy.

## Tool Updates
- Fixed minor bugs in GATE (similar issue as **`DumpImportTable`**)


# 2022-09-24 Changes

## Patch Updates
- Updated Chris' lua override patch to work with a mapping file and work properly on more recent clients.

## Script Updates
- Added **`LUA.loadLuaAfter`** function to support the branched loading in recent clients (used by `AddLuaOverrides` patch)


# 2022-09-24 Changes

## Patch Updates
- Added new module for capturing session value & related functions

- Added new patches to

	- Enable preview for equipments in Trader cash shops. Requires 2017+ clients.
	
	- Customize guild emblem file size.
	
	- Customize error message displayed when client runs without launcher.
	
	- Customize tax value used for mail (Rodex)
	
- Adapted some patches for latest clients (more to come soon).

- Updated copyright date for a few patches (more to be updated soon).


# 2022-09-08 Changes

## Patch Updates
- Updated [Skill spam patch for newer clients](https://github.com/Neo-Mind/WARP/issues/102).

- Updated copyrights for all patch definition yml files.

- Updated [Disable Gameguard patch for 2022 clients](https://github.com/Neo-Mind/WARP/issues/95)


# 2022-09-06 Changes

## Patch Updates
- Fixed [bug with Custom Captcha decompression patch](https://github.com/Neo-Mind/WARP/issues/103)


# 2022-08-24 Changes

## Extension Updates
- Updated **`Extract msgstringtable`** extension for latest client.


# 2022-08-23 Changes

## Patch Updates
- Fixed [crashes with Custom Shield patch](https://github.com/Neo-Mind/WARP/issues/97)

- Fixed [crashes with Custom Font Height patches](https://github.com/Neo-Mind/WARP/issues/92)

- Added patch to [Disable password encryption in login packet for new clients](https://github.com/Neo-Mind/WARP/issues/94)

- Fixed [conflict in Shared head palette patches](https://github.com/Neo-Mind/WARP/issues/84)

- Updated Lua files for Custom Job patch with [missing entries for new jobs](https://github.com/Neo-Mind/WARP/issues/98)
  and [correct mappings for doram race](https://github.com/Neo-Mind/WARP/issues/96)
  
- Partially fixed Gameguard patch. Still needs more work. 

- Removed unnecessary parseInt calls from scripts.

## Script Updates
- Updated **`ReloadPatch`** function to return the value of the called patch function.


# 2022-04-03 Changes

## Patch Updates
- Added new patches.
	- [Case-Insensitive cash shop search](https://github.com/Neo-Mind/WARP/issues/13)
	- [Enable "Notice" email section](https://github.com/Neo-Mind/WARP/issues/41)

- Added the start date for "No Color" translation.

## Script Updates
- Added **`PUSH_STR`** function to perform a `PUSH+JMP` for pushing strings .


# 2022-02-23 Changes

## Patch Updates
- Fixed crash in **`Custom Job`** patch.

- Fixed [issue in Draw Shield on Top patch](https://github.com/Neo-Mind/WARP/issues/83)

- Updated **`Disconnect to Login Window`** patch [for newer clients](https://github.com/Neo-Mind/WARP/issues/81)

- Fixed [bug in Increase Zoom Out patch](https://github.com/Neo-Mind/WARP/issues/44).


# 2022-02-22 Changes

## Patch Updates
- Updated LUA files for **`Custom Job`** patch.

- Added new translation [as requested](https://github.com/Neo-Mind/WARP/issues/89)

- Updated Custom Path patches to handle the various suffixes with a slightly better approach.


# 2021-12-29 Changes

## Tool Updates (v1.5.3)
- Fixed Bug in `Exe.Allocate` function when no active patch is available.

- Fixed `Exe.FindFunc` function to use look up table instead of thunk table.

- Fixed issue with `Drag & Drop` for Session files & Tester Directory.


# 2021-11-26 Changes

## Patch Updates
- Fixed the following patches for latest clients (2021-11-10+)
	- **`Enforce 0 C in Cash Shop`**
	- **`Custom Exp Bar Limits`**
	- **`Enable Custom Homunculi`**
	- **`Enable Custom Jobs`**
	- **`Enable Custom Shields`**
	- **`Allow 65k hair styles`**
	- **`Increase hair styles`**
	- **`Always see hidden/cloaked objects`**
	- **`Load iteminfo per server`**
	- **`Always load korea ExternalSettings lua file`**
	- **`Remove Adventurer Agency from party`**
	- All path customization patches

- Disabled **`Translate Taekwon`** patch for new clients, since it is picked up from msg table and therefore can be altered there instead.

- Fixed bug in **`Custom Font Weight for all`** patch


# 2021-11-11 Changes

## Patch Updates
- Fixed bug in **`Custom MerchantURLs`** patch.


# 2021-11-04 Changes

## Patch Updates
- Fixed [bug in Enable Proxy Support patch](https://github.com/Neo-Mind/WARP/issues/80)
- Fixed [bug in Allow Guild activities in clan patch](https://github.com/Neo-Mind/WARP/issues/75)

# 2021-10-29 Changes

## Script Updates
- Updated **`AutoHook`** function to allow for multiple from addresses & source offset(s). Also added 'this' pointer support for post processing function.


- Added **`MultiAlloc`** function to perform contiguous DIFF allocation for storing multiple values. It accepts the sizes needed and returns corresponding **`VIRTUAL`** addresses.


# 2021-10-28 Changes

## Patch Updates
- Fixed the order in `Enable Multiple GRFs` patch.


# 2021-10-27 Changes

## Tool Updates (v1.5.2)
- Added Drag & Drop support for the tools.
	- You can drop `Exe files` or `Session YAMLs` directly on the [Main GUI] for them to be loaded. 

	- Similarly you can drop the `Test Folder` or `Session YAMLs` in  [Test Bench]

	- Also, you can drop any files/folders into the various editor frames and text boxes to get their paths added directly.

- `Exe.FindSpace` function has been changed to `Exe.Allocate` and it always reserves the space allocated now. 

- Continuing from the above change, `Exe.Add*` functions no longer takes the target address as an argument. Please use the `Exe.Set*` functions instead on `allocated` addresses.

- If the value going to be added is already known, then use the `Exe.Add*` functions to stage the addition to the `DIFF` section and use it's return value (addresses & size - similar to `Exe.Allocate`). 

- `Exe.ProtectChanges` function has been split into `Exe.ConcealChanges` and `Exe.RevealChanges` respectively and they both take a password now.

- Added caching support to `Exe.FindFunc` to avoid repetitive searches for the same function later.

- Fixed bug with dependency chain not ignoring invalidated patches.

- Added type information to input values in Session files.

- Added support for `init` member function on Patch functions which will get executed when a client is loaded.

- Added support for `initvars` and `clearvars` member arrays on Patch functions to hold the name of member variables to be initialized/purged when a client is loaded.

  `initvars` need to be of the form `["name1", value1, "name2", value2...]`

## Script Updates
- Fixed bug in **`UserChoice`** function

## Patch Updates
- Updated patch **`Enable DNS Support`** to fix[Issue #77](https://github.com/Neo-Mind/WARP/issues/77)


# 2021-10-26 Changes

## Script Updates
- Added new function **`AutoHook`** to group together all the common steps involved in hooking & addition of code.


# 2021-10-22 Changes

## Script Updates
- Added new function `AttachCode` to group together all the common steps involved in hooking & addition of code.


# 2021-10-06 Changes

## Patch Updates
- Minor correction in `Font Height` patch script


# 2021-10-04 Changes

## Patch Updates
- Added patch to disable pkt encryption for login/char

- Fixed issue with `Auto mute` patch


# 2021-10-03 Changes

## Patch Updates
- Updated the Lua files used with `Custom Jobs` patch

- Added patch to fix the alignment & bg issue with recent 'New Character' window.


# 2021-10-02 Changes

## Patch Updates
- Updated `Customize Walk delay` patch to set individual delays.

- Added patches for the following:

	- More `Font customization` options i.e. weight (fixed and specific to normal & bold), charset, relative height & weight
	
	- Play sound instead of displaying `MessageBox`
	
	- Show icon inside `MessageBox`
	
	- Skip showing `MessageBox` altogether
	
	- Borderless full screen
	
	- Setting Mini title bar
	
	- Ignoring Debugger presence

	- Add Input Delay
	
	- Change Game Loop delay

	- Altering priority from (Idle to Normal) or (Normal to High)
	
	- Changing Captcha decompression size
	
## Script Updates
	- Added new function `GetImpRefs` to get references of Imported function
	
	
# 2021-09-26 Changes

## Patch Updates
- Added patch to `Customize Auto follow stop delay`.

## Tool Updates
- Fixed number input issue in session files.

- Modified `Exe.FindSpace` function to include the size allocated as the 3rd element in the returned list.

- Added `Exe.Reserve` function for performing allocation + reserve address in DIFF section without needing to set any data.

- Added variants of `Exe.Add*` functions which performs the allocation along with insertion and returns the addr & size list identical to `Exe.FindSpace`.


# 2021-09-11 Changes

## Patch Updates
- Added temporary fix for integers being loaded as strings from session files.
  Fixes [bug with Custom Jobs patch](https://github.com/Neo-Mind/WARP/issues/73)


# 2021-08-31 Changes

## Patch Updates
- Fixed bug with Custom Font Name patch

## Tool Updates
- Fixed 1 non-critical issue with the GATE dll

# 2021-08-27 Changes

## Patch Updates
- Fixed [bug with MonSizeEffect lub patch](https://github.com/Neo-Mind/WARP/issues/70)

- Fixed [bug with Hide Packets from PEEK patch](https://github.com/Neo-Mind/WARP/issues/68)

- Fixed [bug with Restore model culling patch](https://github.com/Neo-Mind/WARP/issues/67)

- Fixed [bug with New Button visibility patch](https://github.com/Neo-Mind/WARP/issues/72)

## Script Updates
- Renamed the `self_call` sub function to `self`

## Tool Updates
- Added `Warp.BlockMsgs` & `Warp.AllowMsgs` function to allow partial logging.


# 2021-08-26 Changes

## Script Updates
- Added extra functions to `Function`, `Map` & `Set` types.

	| Function           | Description |
	| ----------------   | ----------- |
	| `<map>.open`       | Provides a proxy for destructuring the keys out similar to an `Object` |
	| `<map>.hasValue`   | Check if the map has the specified value (alternative to the `has` function |
	| `<set>.get`        | Retrieve a value using it's index |
	| `<func>.call_self` | Enables call a function with itself as the `this` pointer |

- Added `MakeMap` function to create a `Map` object in a clearer form.

- Added `ReloadPatch` function to clear & load an already selected patch.

- Fixed bug in `OpData` class for 1 of the Scale index forms.

- Fixed bugs in some instruction generators.
 
## Patch/Extension Updates
- Started using all the new features in all the patches & extensions.

## Tool Updates
- Added 2 new options related to errors in [Test Bench].

	- `Show only errors & warnings` => As the name sounds, it allows for skipping 'success' & 'ignored' messages for each individual patch/extension during tests.
	
	- `Show lines with error` => Option to display the linenumber & filename from where the error originated.

- Modified the way the exe file names are displayed during test => Now the test directory being used is displayed first and only the filenames are reported seperately.


# 2021-08-22 Changes

## Script Updates
- Added `PatchReporter` function which uses the logging mechanism to report the changes staged by the tool. 

- Moved most of the `Init` scripts into Modules.

- Added a new `CACHE` module for storing data persistent per session i.e. It will remain in there as long as you don't load a new client.
  
  The module also helps with setting up shared data & changes amongst related patches by means of multiple Vaults & a User Registration system.

## Tool Updates
- Added `Exe.HasTag` function to check for existing tags.

- Enabled the use of `this` pointer in all the patch & extension functions. It will point to the main function for each.

- Modified the change reporting mechanism to use a Scripted function called `PatchReporter` instead.

- Now evaluation errors displays the line number & filename the error came from properly.


# 2021-08-20 Changes

## Script Updates
- Shifted `Log` and `OpCodeList` to module files

- Added depth settings to `Log` for hiding unnecessary level of support function logs. All the support functions have been updated.

- Added `getReg` functon to `ModRM` and `SIBase` classes to get their respective member registers quickly.

  It accepts 1 letter as argument ('R' & 'O' for `ModRm` , `I` & `B` for `SIBase`)

- Added `PH_Regs` map to get Placeholder registers quickly based on bit sizes.

- Removed `TAB` constant since it is not needed anymore.

- Shifted some of the content in initialization scripts into modules.


# 2021-08-19 Changes

## Tool Updates
- Changed the root node of **`Patches.yml` & `Extensions.yml`** to a map. No more hyphens needed for Group names and Extension names.

- Added support for including/importing additional YAML files into current one for **`Style` & `Language`** files as well as **`Patches.yml`** by means of the **`include`** key.

  It can be either 1 name of list of names. 
  
  **`Extensions.yml` do not have it yet since it will rarely get big enough to split into multiple files.**

- Session files now also records the selected **`extensions`**, the **`Test Dir`** as well as the selected **`tester exes`** when saving the file in [Test Bench].

  This will help to quickly start the tests when re-launched, instead of selecting everything again from scratch.

- Updated the inbuilt extension for converting NEMO profiles to WARP session files. Inputs are also mapped properly now (aside from **`D_MultiChoice`**).

- Fixed issue with session file generation of **`Target Exe`** when the option is enabled.

- Added support for fully encrypted scripts with the suffix **`.ejs`**. It can also have an optional disclaimer/license header.

  **Do not try to create this manually.**
  
- Added **`Warp.EncryptFile`** function for generating **`.ejs`** files from the specified source file. Any disclaimer/license header present will be retained as is.

- Added **`Warp.LoadEJS`** function for loading **`.ejs`** files explicitly from scripts or the **`Script Editor`**.

- Added support for module scripts with the suffix **`.mjs`**.

	- Modules are a handy way of encapsulating 'Singleton' objects and as such you are likely to see more use of these in future.

	- The name of the module can be defined inside the **`.mjs`** file by adding the following in a seperate line:

	   `// MODULE_NAME => put_the_name_here`

	- In case this line is not there, then the tool will use the **basename** of the file as the module name.

	- Be aware that modules only get loaded once and the variables exported can only be updated from within the module.

	- Since the loading process is different, module scripts cannot be encrypted into **`.ejs`**.


# 2021-08-18 Changes

## Tool Updates
- Added overload of **`Exe.FindHexN`, `Exe.FindLastHexN`, `Exe.FindTextN` & `Exe.FindLastTextN`** functions to accept a `min`, `max` pair as the count.

  These will return an empty list if the number of elements are < `min` or > `max`.

- Fixed bugs and modified the inner workings of **`D_Color`** type. It only takes the following constraints now:

	- `format` => Previously called `order`. Indicates the format in which the components need to be kept from MSB to LSB.

	- `R`, `G`, `B` & `A` => Optional keys to set the default value for any missing components in the format (need this for the color `ColorPanel` being displayed).
	
- Similarly the color value can be provided in one of 3 forms:

	- `[component list]` => The components need to follow the `format` specified. i.e. for `RGB`, it should be [r,g,b]

	- `0xnumber` => Same point here the bytes need to follow the `format` specified from MSB to LSB

	- `'#hexcode'` => Standard coloring hex code . The `format` is only used for determining the internal byte representation.

- Changed `align` constraint to `pad` for string types. 

- `align` constraint now represents the horizontal alignment of the string values inside the respective textboxes of the **`Input Dialog`**


# 2021-08-17 Changes

## Tool Updates
- Fixed the visual bug with List Panel (used for **`D_Choice & D_MultiChoice`** types) where the frame was coming out and the window just kept enlarging too much.

- Disabled the corner size-grips from going beyond specified `maxWidth` & `maxHeight` if any.

- Added a **"Global"** patch that is now available by default when an exe is loaded.

	- The purpose of this patch is to allow for a common patch to stage changes shared by multiple patches.

  	- Therefore it will not be available for selection in the **`Patch List`**.

- Added **`Exe.ActivateGlobal` & `Exe.ClearGlobal`** functions to work with the aforementioned **"Global"** patch (as counterparts to **SetActivePatch** & **ClearPatch**.

  These also selects & deselects the **"Global"** patch respectively unlike their counterparts.

- Added **`ActivePatch`** property to **`Exe`** object which reflects the name of the currently active patch.

  You can also set it directly instead of using **SetActivePatch** function.

- **`Exe.ClearPatch` & `Exe.SetActivePatch`** can now be invoked without arguments. Behavior for empty argument is as follows:

	- **`Exe.ClearPatch`** => will clear the changes in the active patch.
	
	- **`Exe.SetActivePatch`** => will keep no patch as active. Same thing happens if you assign **`Exe.ActivePatch`** member directly.

- Added **`Exe.UndoChanges`** function to revert the changes setup for a range of addresses.

- Added **`Exe.FreeUp`** function to revert the changes setup & free up a range of addresses from `DIFF` section.

- Added **`Exe.BeginTag` , `Exe.EndTag` , `Exe.DelTag`** for associating tag names with set of changes & address reservations (in `DIFF` section) to tag names.

	- The first 2 are used to mark the beginning & ending of the tagging process.

	- If **`Exe.BeginTag`** is again invoked with the same name, the previous changes gets wiped (and you can optionally `FreeUp` any reservations too).

	- The 3rd one is for deleting a tag. With this you have the option of either preserving or discarding the staged changes & reservations respectively.


# 2021-08-16 Changes

## Tool Updates
- Added overloads for **`Warp.Define` , `Warp.Encrypt` & `Warp.Execute`** functions to accept list of strings (which gets concatenated internally).

- Added support for links in titles, tooltips & descriptions of **`Patch List & Extension List`** (latter only makes sense while testing though).

- A `linkText` key is now available for specifying color for these link texts (items in the lists) inside a **`Style file`**

- Right clicking on the items in **`Patch List, Extension List & Exe List`** will now copy the details to the clipboard.

- All **`patch`** functions & sub-functions as well as **`extension`** functions get their respective titles as optional 2nd argument now.

- Added **`allowSkip`** key for use in **`Patches.yml` & `Extensions.yml`** to allow skipping of patches & extensions respectively without reporting it as a warning.

  The **`SkippedPatches.log`** file will still have the details.

- Fixed the issue where patches & extensions could not be fully empty.

  Now you can just specify the `<name>` alone without any keys attached to use the defaults for the other details.

- Fixed the issue with `Ctrl+Q` interruption mechanism.

- Fixed the issue with empty string auto-returning false for all the string types in **`Exe.GetUserInput`**

- Modified the usage of **`D_Hex`** type. Now it only has 2 constraints to guide it

	- **`endian`** => Indicates the endianness of the displayed values. This can be either `little` or `big` . Default is `big` .
	
	- **`byteCount`** => The number of bytes expected to be stored. Default is 1

- Added optional `stepSize0`, `stepSize1`, `stepSize2` & `stepSize3` constraints to use for the respective individual elements of **`D_Vec\*`** types.

- Enabled global `min`, `max` and `stepSize` constraints to **`D_Vec\*`** as well.

  If the individual constraint is not available, the elements will pick up these.

- The escape characters `\n` and `\t` now gets displayed properly in the **`Output`** section. Same goes for blank spaces.

- Added `maxWidth` and `maxHeight` constraints in the **`Input Dialog`** for all types.

- Added **`Warp.clearEditor` & `Warp.clearOutput`** functions for clearing the **`Script Editor` & `Output`** sections respectively from Scripts or the editor itself.

  **Please note that the starting letter is small unlike other functions** (need this way, since these serve as signals)


# 2021-08-15 Changes

## Tool Updates
- Added option in the **`Settings`** dialog to show the modifications setup via **`Exe.Set\*` & `Exe.Add\*`** functions.

- Added **`Exe.ProtectChanges`** function to selectively avoid the above switch when needed. It gets automatically re-enabled when the patch/extension function call is over. 

- Added **`Exe.SetFloat` & `Exe.GetFloat`** functions. Also added **`Exe.SetBytes`** function for list of bytes.

- Added **`Exe.Add\*`** variants of all the numeric types (including float) as well as list of bytes.


# 2021-07-31 Changes

## Patch Updates
- Fixed the remaining [issue with Increase Hair style patches](https://github.com/Neo-Mind/WARP/issues/56).


# 2021-07-29 Changes

## Patch Updates
- Corrected 1 issue in "Add Chris' lua overrides" patch.

- Divided the HP bar resize patch for mobs into 3 => 1 for Normal, 1 for Mini-Boss and 1 for Boss monster respectively.

  Now no more [conflicts about the health bar](https://github.com/Neo-Mind/WARP/issues/57).

- Fixed the [byte order issue in Packet Key patches](https://github.com/Neo-Mind/WARP/issues/55). 

  The `PACKET` object now better recognizes patched clients and `Get Packet Keys` extension works correctly for patched clients too.


# 2021-07-25 Changes

## Patch Updates
- Rearranging some codes and using `const` where appropriate.

## Tool Updates
- Added `findAs` function to `Array` types as an extended version of `find`. The function provided as argument can return the result required instead of `true`.

- Forgot to identify `GetInstr` function earlier. Fixed now.


# 2021-07-24 Changes

## Patch Updates
- Fixed [issue in Packet key patches](https://github.com/Neo-Mind/WARP/issues/55) for latest clients.

- Fixed [issue with Resize MVP health bar](https://github.com/Neo-Mind/WARP/issues/57).

## Tool Updates
- Corrected 1 bug in `OpData` class.


# 2021-07-23 Changes

## Patch Updates
- Updated patches using the placeholder functions to remove the deprecated functions.

- Minor cleanup also being done (using `const` and swapping out `forEach` with `for of`)

## Extension Updates
- A little bit of cleanup (using `const` and swapping out `forEach` with `for of`)


# 2021-07-22 Changes

## Patch Updates
- Converted a lot of `let` to `const`

- Changed some of the `forEach` functions to `for of` loops.

## Tool Updates
- Changed the placeholder functions to use `_` & `_.` instead of `?` to avoid clashing with regular wildcards.

- Removed `SwapFiller` & `SetFillTarget` function (kind of redundant with the other one without much benefits).

- Changed the way the byte count is sent to `SwapFillers` and `SetFillTargets`, now the byte count can be clubbed with the index as a string key => `"index, bc"`

- Also, for `SetFillTargets`, the starting address needs to be provided in the map argument itself using the key `start`. If it's not there then `0` is assumed.

- Converted a lot of `let` to `const`

- Changed some of the `forEach` functions to `for of` loops.

- Changed `LOCK`, `REPE` & `REPN` to `ILOCK`, `IREPE` & `IREPN` respectively. The first 3 are now functions instead to automatically prefix these values.

  `REP` function has also been provided as an alias to `REPE`. Check the wiki for more details. 

- Added string instructions to use with the `REP*` functions.

- Updated **'Init'** scripts to reflect the changes in placeholder functions.


# 2021-07-15 Changes

## Patch Updates
- Added patch for [Chris' lua overrides](https://github.com/llchrisll/ROenglishRE/tree/master/Custom%20Lua%20Files)

## Extension Updates
- Bug fix (Changed all the wrong `CaseInsensitive` names to `CASE_INSENSITIVE`).

- Added the missing `_` variable in `GenMapEffectPlugin.qjs`


# 2021-07-12 Changes

## Patch Updates
- Fixed bug in [Disable Multiple Windows](https://github.com/Neo-Mind/WARP/issues/52) patch.

- Some minor cleanup.


# 2021-07-07 Changes

## Patch Updates
- Fixed issue with doram palette in **`Increase Hairstyle`** patches.

- (Hopefully) Fixed the rendering bug with [Increase Zoom](https://github.com/Neo-Mind/WARP/issues/44) patches.

## Tool Updates
- Added thai language file with translations for the new entries.

- Changed the pattern for 1 byte fillers to use `?.` prefix . The earlier pattern was creating chaos when the bytes are clubbed together.


# 2021-07-06 Changes

## Tool Updates
- Added [Exe.ClearSavedInput](https://github.com/Neo-Mind/WARP/wiki/Exe-Object#patch-related) for clearing existing inputs. Useful in Test Bench.

- Fixed the bug with WARP crashing when running **`Exe.GetUserInput`** from [Script Window](https://github.com/Neo-Mind/WARP/wiki/Script-Window).


# 2021-07-05 Changes

## Patch Updates
- Converted comments in all the patch scripts to use `$$` function for optional reporting.

## Tool Updates
- Added few instruction constants.

	- **`FP_START`** = Frame pointer begins (`push ebp` followed by `mov ebp, esp`)
	
	- **`FP_STOP`**  = Frame pointer ends (`mov esp, ebp` followed by `pop ebp`)
	
	- **`POP_EAX`**  = Obvious no?
	
	- **`CDQ`**
	
	- **`INT3`**

- Changed [Exe.IsSelected](https://github.com/Neo-Mind/WARP/wiki/Exe-Object#patch-related) function to [Warp.GetPatchState](https://github.com/Neo-Mind/WARP/wiki/Warp-Object#functions) for logical reasons.

- Changed [Exe.TestMode](https://github.com/Neo-Mind/WARP/wiki/Exe-Object#properties) to [Warp.TestMode](https://github.com/Neo-Mind/WARP/wiki/Warp-Object#properties) as well.

- Added 2 functions for displaying messages from patch/extension scripts.

	- **`Warp.InformUser`** = Used for information messages
	
	- **`Warp.WarnUser`**   = Used for warning messages

- Added support for user interrupts with **`Ctrl+Q`** sequence while selecting multiple patches in [Main GUI] and running tests in [Test Bench].

- Added switches for **`RegEx`** & **`Case sensitivity`** in all the filter and search inputs.

- Updated **`Dark_Mode`** style for the new entries in UI (for e.g. the filter/search options).

- Updated the templates for [Language](https://github.com/Neo-Mind/WARP/wiki/Language-File) & [Style](https://github.com/Neo-Mind/WARP/wiki/Style-File) files.


# 2021-07-02 Changes

## Tool Updates
- Removed [NO_ALLOC](https://github.com/Neo-Mind/WARP/wiki/Scripted-API#strings--error-messages) constant since it is no longer needed.

- Changed the pattern generated by [Filler](https://github.com/Neo-Mind/WARP/wiki/Scripted-Functions#filler-functions) function for bc = 1. Now it looks like ?01 and ?121 etc.

- Added the reflection options in [Instr](https://github.com/Neo-Mind/WARP/wiki/Instr) class and [CaseAddr](https://github.com/Neo-Mind/WARP/wiki/Scripted-Functions#extractors) function.

- Added [Exe.GetSavedInput](https://github.com/Neo-Mind/WARP/wiki/Exe-Object#user-input) function to retrieve the value of a previously saved user input (either obtained from `session file` or using [Exe.GetUserInput](https://github.com/Neo-Mind/WARP/wiki/Exe-Object#user-input)

- Added support for encrypted scripting. To achieve this, following 3 functions have been added:

	- **`Warp.Encrypt`** = Converts a script code into it's equivalent encrypted bytes. Output is in hex form.

	- **`Warp.Execute`** = Evaluates the provided encrypted hex in the underlying JS engine and return the result.

	- **`Warp.Define`**  = Execute the provided encrypted hex and assign the result to the specified global variable. Returns false if an error occured or if the result was `undefined`.

- Added **`UserChoice`** function as a quick wrapper for yes/no questions to user. Primarily used in extensions.

- Converted comments in all the initialization scripts to use `$$` function for optional reporting. Should be helpful for debugging in future.

## Extension Updates
- Converted comments in all the extension to use `$$` function for optional reporting. Should be helpful for debugging in future.


# 2021-06-30 Changes

## Tool Updates
- Modified Language **`translations`** to check for **`find`** patterns case-insensitively.

- Fixed bug with filters not looking for translated text. Now they will look for both translated & original texts.

- Fixed bug with **`D_Color`** type when returning default value.


# 2021-06-26 Changes

## Tool Updates
- Added *numeric vector* input [DataTypes](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#datatype)

	- **`D_VecI8, D_VecI16, D_VecI32`**

	- **`D_VecI8, D_VecI16, D_VecU32`**

	- **`D_VecF`**
	
- All the **`D_Vec`** can have upto `4` elements. The size is determined by the default value provided.

- All of them have individual constraints for setting **`min & max`** values as well as specifying a **`name`**.

  For e.g. `index 1` can be setup as `min1: 3, name1: "X Coord"`. If the `name` is not provided then it defaults to `Index1`


# 2021-06-25 Changes

## Tool Updates
- Added `view` button along with `browse` button for [D_InFile & D_OutFile](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#datatype) types to open currently specified filename.

- Fixed bug with saving user inputs of [D_Choice & D_MultiChoice](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#datatype) types.


# 2021-06-24 Changes

## Tool Updates
- Added reflection support to all the **`Exe.Get`** functions

	- i.e. any existing changes staged by patches can now be `reflected` while retrieving the values.

	- To do this an additional (optional) boolean argument has been added to all of the **`Exe.Get`** functions.
	
- Renamed **`D_List & D_MultiList`** types to [D_Choice & D_MultiChoice](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#datatype) respectively.

	- Also added `Selected value` display and filtering support (similar to `Patch List`) for both of them.


# 2021-06-23 Changes

## Tool Updates
- Added [Warp.SetPatchState](https://github.com/Neo-Mind/WARP/wiki/Warp-Object#functions) function for updating the 'selection' state from script.

- Added dependency chain support (using **`'needs'`** key in **`Patches.yml`**

- Added case-insensitive search option to [Exe.FindText & Exe.FindTextN] functions (only for default encoding i.e. [ASCII](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#encoding)).

	- [CASE_SENSITIVE & CASE_INSENSITIVE](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#sensitivity) keywords have been added to support this.


# 2021-06-22 Changes

## Tool Updates
- Added **`D_Float`** user input [DataType](https://github.com/Neo-Mind/WARP/wiki/Inbuilt-API#datatype)

- Added **`'stepSize'`** constraint for all numeric inputs.

- Added [System.Trash](https://github.com/Neo-Mind/WARP/wiki/System-Object#modifications) command for moving files to `Recycle Bin`

- Added an optional ***`Build Version`*** display in [Main GUI]

- Added **`Settings`** dialog containing the following options & buttons :

	- [Main GUI]

		- Option to show `Build Version` along with `Build Date`.
		- Option to enable/disable usage of EPI.
		- Option to enable/disable generation of .secure.txt file along with **Target Exe**.
		- Option to enable/disable generation of session files along with **Target Exe**.
		- Option to keep the inputs as-is while loading session files.
		- Button for saving current resolution of **Main & Script** windows as the default.
		
	- [Test Bench]

		- Option to keep the inputs as-is while loading session files.
		- Option to stop running tests when the first error is encountered.
		- Button for saving current resolution as the default.


# 2021-06-21 Changes

## Tool Updates
- Added **`Settings`** & **`Donate`** buttons to both GUIs

- Modified [Exe.FindSpace](https://github.com/Neo-Mind/WARP/wiki/Exe-Extractors#content-query) function to return **`[PHYSICAL, VIRTUAL]`** address pair

- **`Exe.FindSpace`** also throws an error automatically in case it fails.


# 2021-06-20 Changes

## Patch Updates
- Slightly changed the title of **`OpenToServiceSelect`** patch.

- Added patches to

	- Restore Auto Follow

	- Hide Ingame Windows

	- Draw Shield on Top

	- Fix Achievement Counters

## Tool Updates
- Updated [SwapFiller & SetFillTarget] functions to accept array of strings.

- Added **`IsMain`** property to **ROC** object to indicate that the client is Main one (i.e. neither RE nor Zero type).


# 2021-06-17 Changes

## Patch Updates
- Added patches to

	- Enable Custom Homunculi

	- [Fix homunculus attack AI](https://github.com/Neo-Mind/WARP/issues/38)

	- Send client flags

	- Allow all items in Shortcut

	- Remove Adventurer Agency from Party

	- Fix Charset for Fonts

	- Customize Merchant store URL

	- Hide packets from PEEK

	- Use 'identified' drops for Boss (MVP) mob
	
- Added cleanup function to PreviewInShop to work with Send Client Flags patch

- Started fine tuning & comment fixes in scripts

- Updated some of the entries in Patch list (Patches.yml)


# 2021-06-14 Changes

## Patch Updates
- Added patch to [Enable item preview in Cash Shop](https://github.com/Neo-Mind/WARP/issues/17).

- Added patch to Decrease the zoom to 25% of Maximum.

- Fixed 1 remaining bug with Hide Buttons patch for new UI for slightly older clients.

## Tool Updates
- Fixed 1 bug in **`<number>.toIEEE`** function for conversion of float to IEEE hex string.


# 2021-06-12 Changes

## Patch Updates
- Added patch to [Enable Custom Player Skills](https://github.com/Neo-Mind/WARP/issues/25).

## Tool Updates
- Updated signature of [SwapFiller & SetFillTarget] functions to accept index & bytecount together as a tuple (2 element array).


# 2021-06-11 Changes

## Patch Updates
- Added patch for [Opening to Service Select from login screen](https://github.com/Neo-Mind/WARP/issues/35) in latest clients.

- Added patch for [Restoring Songs Effects](https://github.com/Neo-Mind/WARP/issues/36)

- Fixed bug in [Selected Login Background](https://github.com/Neo-Mind/WARP/issues/33) patch.

- Fixed bug in [Hide Buttons patch for new UI](https://github.com/Neo-Mind/WARP/issues/32).

- Fixed bug in [Custom Shields patch](https://github.com/Neo-Mind/WARP/issues/37) related to showing two handed weapons.

- Fixed bugs in **`Show Exp Numbers`** patch. Thanks [@Haziel](https://github.com/SirHaziel) for pointing it out.

## Tool Updates
- Slight update to **`LUA.addLoaders`** function to report the reference lua file name (in case it fails)


# 2021-06-10 Changes

## Patch Updates
- Made the higher limit of **`Custom Jobs`** patch a user input (restricted to max of `5000`).

- Fixed the [arrow translations](https://github.com/Neo-Mind/WARP/issues/24). Since we are restricted to ASCII table, the best resembling values were picked from them.

- Fixed remaining [bugs in Increase Hairstyle patches](https://github.com/Neo-Mind/WARP/issues/16) (hopefully I have covered all the missed tables now)

- Updated **`Shared Head palette`** patches to work well with **`Increase Hairstyle`** patches. 

- Fixed the **`Shared Body palette`** patches for costume palettes and doram palettes. 

- Corrected descriptions for **`Shared Head palette`** patches & **`Translate Arrows`** patch.

## Tool Updates
- Updated **`LUA.addLoaders`** with option to load the reference lua file either before or after the new ones. You can also completely skip it.


# 2021-06-05 Changes

## Patch Updates
- Fixed final [bug with Custom Vending Limit](https://github.com/Neo-Mind/WARP/issues/15) patch that was present in newer clients.

- Fixed 1 typo in **`Patches.yml`** (thanks [@Everade](https://github.com/Everade) for pointing it out).

- Fixed titles for user inputs in **`Resize \* Box`** patches.

- Fixed 1 typo in [Translate arrows to English](https://github.com/Neo-Mind/WARP/issues/24) patch. But still the arrows arent correct.

## Tool Updates
- Added link to Changelog in [README](README.md).


# 2021-06-03 Changes

## Patch Updates
- Added patch to [Show Damage for GvG](https://github.com/Neo-Mind/WARP/issues/23).

- Added patch to [Translate arrows to English](https://github.com/Neo-Mind/WARP/issues/24).

- Fixed issues with **`Packet Key`** patches.

- Fixed [issue with Custom Vending Limit](https://github.com/Neo-Mind/WARP/issues/15) patch.

- Fixed [issue with Custom Walk Delay](https://github.com/Neo-Mind/WARP/issues/26) patch.

- Fixed [issue with Close Cutin on Esc key](https://github.com/Neo-Mind/WARP/issues/28) patch.

- Updated the translation made by [@Everade](https://github.com/Everade).

## Extension Updates
- Fixed problem with **`Get Packet Keys`** extension (now it is able to get the keys from patched clients as well).

[Main GUI](https://github.com/Neo-Mind/WARP/wiki/Main-GUI)
[Test Bench](https://github.com/Neo-Mind/WARP/wiki/Test-Bench)
[SwapFiller & SetFillTarget](https://github.com/Neo-Mind/WARP/wiki/Scripted-Functions#filler-functions)
