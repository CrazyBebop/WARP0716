--[[
  CustomJobs Lua Data
  Author: CrazyBebop
  Last Modified: 2026-03-16
]]--

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
-- Read when you APPLY the WARP patch (2026-09-02), not by the client: WARP bakes every
-- quoted row into the patched exe, after the five official 2025 jobs. Re-apply WARP after
-- editing this file. An inheritance form like the two below means stock (Novice) hands
-- and adds no row; that is right for this example, which ships no weapon sprites.
-- A quoted folder name is a row:  PCHands[PCIds.EXAMPLE_JOB] = "example_job"
-- and expects data\sprite\<race>\example_job\example_job_<gender>_<weapon>.spr to exist.
PCHands[PCIds.EXAMPLE_JOB] = (PCHands[PCIds.NOVICE] or "")
PCHands[PCIds.EXAMPLE_JOB_B] = (PCHands[PCIds.NOVICE] or "")
