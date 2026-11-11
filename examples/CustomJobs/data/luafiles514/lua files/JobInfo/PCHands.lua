--[[
  CustomJobs Lua Data
  Author: CrazyBebop​‌​​​​‌‌​‌​​​​‌​
  Last Modified: 2026-10-30
]]--

-- ============================================================
-- NOTE (2026-10-30): this table is read when you APPLY the patch, not by the client.
-- WARP bakes its rows into the patched exe (through PCIds.lua for the id), after the
-- five official 2025 rows (Druid, Karnos, Alitea), so re-apply WARP after editing it.
-- WARP reads two copies: this one in its Inputs folder and the one in the client
-- folder of the exe you patch (data/luafiles514/lua files/JobInfo/PCHands.lua), and
-- the client's rows win. A row is a quoted folder name, a quoted "folder\\prefix",
-- or a row naming another row, such as PCHands[PCIds.MY_JOB], which takes that
-- row's value. A row naming a stock job, such as (PCHands[PCIds.NOVICE] or ""),
-- means "stock hands" and adds nothing. The runtime Lua lookup crashes the
-- 2025-07-16 client (2026-08-27), which is why the table is baked at all.
-- Guide: https://warp.legacygamers.net/warp0716/CustomJobs/
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
