--[[
  CustomJobs Lua Data
  Author: CrazyBebop​‌​​​​‌‌​‌​​​​‌​
  Last Modified: 2026-03-16
]]--

-- ============================================================
-- Custom Job Palette Names
-- ============================================================
-- Maps job IDs to palette file prefixes for @dye support.
-- Stock palettes are loaded from GRF.
--
-- Inherit from an existing job:
--   PCPals[PCIds.MY_JOB] = PCPals[PCIds.NOVICE]
--
-- Or use your own custom palette prefix:
--   PCPals[PCIds.MY_JOB] = "my_custom_palette"
--
-- Use numeric ID for stock jobs (PCIds.NOVICE may be nil):
--   PCPals[PCIds.MY_JOB] = (PCPals[0] or "")
-- ============================================================

PCPals = PCPals or {}
PCPals[PCIds.EXAMPLE_JOB] = (PCPals[PCIds.NOVICE] or "")
PCPals[PCIds.EXAMPLE_JOB_B] = (PCPals[PCIds.NOVICE] or "")
