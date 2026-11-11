--[[
  CustomJobs Lua Data
  Author: CrazyBebop​‌​​​​‌‌​‌​​​​‌​
  Last Modified: 2026-03-16
]]--

-- ============================================================
-- Custom Job Display Names
-- ============================================================
-- Stock job names are auto-populated from GRF (via PCFuncs.lua),
-- including their peco / dragon / mado mounted variants.
-- Only add entries here for:
--   1. Custom jobs (required)
--   2. Renaming an existing job (optional)
--
-- Both forms work for renaming a stock job — pick whichever you prefer:
--   PCNames[PCIds.WARLOCK]      = "Dark Wizard"     -- by name
--   PCNames[4055]               = "Dark Wizard"     -- by raw ID
--   PCNames[PCIds.LORD_KNIGHT2] = "Holy Knight"     -- mounted variant
--   PCNames[4014]               = "Holy Knight"     -- same thing, raw
--
-- For custom jobs, use the PCIds constant you defined in PCIds.lua:
--   PCNames[PCIds.MY_JOB] = "My Job"
--
-- Full constant list: see PCIds.lua's auto-populate block, or
-- https://github.com/rathena/rathena/blob/master/src/common/mmo.hpp
-- ============================================================

PCNames = PCNames or {}
PCNames[PCIds.EXAMPLE_JOB] = "Example Job"
PCNames[PCIds.EXAMPLE_JOB_B] = "Baby Example Job"
