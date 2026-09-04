--[[
  CustomJobs Lua Data
  Author: CrazyBebop
  Last Modified: 2026-03-16
]]--

-- ============================================================
-- Custom Job Sprite Paths
-- ============================================================
-- Maps job IDs to body sprite folder names.
-- Stock paths are loaded from GRF.
--
-- The value must match your sprite file name (without gender suffix).
-- Sprites go in: data/sprite/�ΰ���/����/
--
-- Example:
--   PCPaths[PCIds.MY_JOB] = "MY_JOB"
--   Expects: MY_JOB_��.spr (male) and MY_JOB_��.spr (female)
-- ============================================================

PCPaths = PCPaths or {}
PCPaths[PCIds.EXAMPLE_JOB] = "EXAMPLE_JOB"
PCPaths[PCIds.EXAMPLE_JOB_B] = "EXAMPLE_JOB"
