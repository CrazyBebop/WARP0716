--[[
  CustomJobs Lua Data
  Author: CrazyBebop​‌​​​​‌‌​‌​​​​‌​
  Last Modified: 2026-09-02
]]--

-- ============================================================
-- NOTE (2026-09-02): this table is read when you APPLY the patch, not by the client.
-- WARP bakes every literal row here into the patched exe (through PCIds.lua for
-- the id), after the five official 2025 jobs (Druid, Karnos, Alitea), so re-apply
-- WARP after editing this file. Only a quoted string is a row: inheritance forms
-- such as (PCHands[PCIds.NOVICE] or "") mean "stock hands" and add nothing.
-- The runtime Lua lookup crashes the 2025-07-16 client (2026-08-27), which is
-- why the table is baked at all. See docs/PATCH_HISTORY.md 2026-09-02.
-- ============================================================
-- ============================================================
-- Custom Job Hand/Weapon Sprite Paths
-- ============================================================
-- Maps job IDs to weapon sprite folder names.
-- Stock hands are loaded from GRF.
--
-- Inherit from an existing job:
--   PCHands[PCIds.MY_JOB] = PCHands[PCIds.NOVICE]
--
-- Or use your own custom hand sprite folder:
--   PCHands[PCIds.MY_JOB] = "MY_CUSTOM_HANDS"
--
-- Use numeric ID for stock jobs (PCIds.NOVICE may be nil):
--   PCHands[PCIds.MY_JOB] = (PCHands[0] or "")
-- ============================================================

PCHands = PCHands or {}
PCHands[PCIds.EXAMPLE_JOB] = (PCHands[PCIds.NOVICE] or "")
PCHands[PCIds.EXAMPLE_JOB_B] = (PCHands[PCIds.NOVICE] or "")
