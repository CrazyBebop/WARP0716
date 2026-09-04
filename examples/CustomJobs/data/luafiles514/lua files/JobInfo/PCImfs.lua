--[[
  CustomJobs Lua Data
  Author: CrazyBebop
  Last Modified: 2026-03-16
]]--

-- ============================================================
-- Custom Job IMF (Animation) References
-- ============================================================
-- Maps job IDs to IMF file prefixes for head positioning.
-- Stock IMFs are loaded from GRF.
--
-- IMPORTANT: Custom jobs REQUIRE actual .imf files in data/imf/
-- Without them, the character will render without a head.
-- Copy an existing job's .imf files and rename them:
--   data/imf/my_job_��.imf  (male)
--   data/imf/my_job_��.imf  (female)
--
-- Inherit from an existing job:
--   PCImfs[PCIds.MY_JOB] = PCImfs[PCIds.NOVICE]
--
-- Or use your own custom IMF prefix:
--   PCImfs[PCIds.MY_JOB] = "MY_CUSTOM_IMF"
-- ============================================================

PCImfs = PCImfs or {}
PCImfs[PCIds.EXAMPLE_JOB] = (PCImfs[PCIds.NOVICE] or "")
PCImfs[PCIds.EXAMPLE_JOB_B] = (PCImfs[PCIds.NOVICE] or "")
