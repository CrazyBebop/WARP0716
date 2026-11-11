--[[
  CustomJobs Lua Data
  Author: CrazyBebop​‌​​​​‌‌​‌​​​​‌​
  Last Modified: 2026-10-30
]]--

-- ============================================================
-- Custom Job Sprite Paths
-- ============================================================
-- Maps job IDs to body sprite folder names.
-- Stock paths are loaded from GRF.
--
-- The value must match your sprite file name (without gender suffix).
-- Sprites go in: data/sprite/인간족/몸통/<남 or 여>/
--   (Korean folder names: human / body / male or female)
--
-- Example:
--   PCPaths[PCIds.MY_JOB] = "MY_JOB"
--   Expects: MY_JOB_남.spr (male) and MY_JOB_여.spr (female)
--
-- A KOREAN name (to reuse a stock sprite, e.g. Swordman's 검사) must reach
-- the client as its Korean (CP949) bytes. Three ways work:
--   PCPaths[PCIds.MY_JOB] = "°Ë»ç"   -- the Latin-1 look-alike older packs use
--   PCPaths[PCIds.MY_JOB] = "\176\203\187\231"   -- the bytes as Lua escapes (검사)
--   or this file saved as Korean / CP949 with "검사" typed in it.
-- "검사" typed in a UTF-8 file does NOT work: use one of the three above.
-- A stock job's body by its PCIds name works too (the patch knows every stock
-- job's folder and its head file); keep "PCPaths = PCPaths or {}" below for it:
--   PCPaths[PCIds.MY_JOB] = PCPaths[PCIds.SWORDMAN]
-- Assignments end without a comma: PCPaths[...] = "..." not "...",
-- ============================================================

PCPaths = PCPaths or {}
PCPaths[PCIds.EXAMPLE_JOB] = "EXAMPLE_JOB"
PCPaths[PCIds.EXAMPLE_JOB_B] = "EXAMPLE_JOB"
