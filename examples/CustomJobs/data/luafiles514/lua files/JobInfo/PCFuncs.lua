--[[
  CustomJobs Lua Functions
  Author: CrazyBebop
  Last Modified: 2026-03-16

  Core helper functions for the CustomJobs system.
  Handles table lookups, inheritance, gender overrides,
  mount IDs, shrink maps, and sprite scaling.

  DO NOT remove functions from this file -- the client
  calls them internally via the CustomJobs binary patch.
]]--

-- ============================================================
-- Table Lookup (used by all Req/Map functions)
-- ============================================================

GetValFromTbl = function(tbl, jobid, lt, isNum, isName)
	if tbl == nil then return (isNum and -1 or "") end

	local rawMode = (jobid > 3950)
	if jobid > 50 and not isName and not rawMode
	then
		jobid = jobid + 3950
	end

	local val
	local ltKey = lt ~= nil and ("LT_" .. lt) or nil
	if tbl[ltKey] ~= nil
	then
		val = tbl[ltKey][jobid]
	end

	if val == nil
	then
		val = tbl[jobid]
	end

	if val == nil
	then
		return (isNum and -1 or "")
	elseif isNum and not isName and val > 3950
	then
		return val - 3950
	else
		return val
	end
end

-- ============================================================
-- Request Functions (called by client for sprite resolution)
-- ============================================================

ReqPCPath = function(jobid, lt)
	return GetValFromTbl(PCPaths, jobid, lt)
end

ReqPCImf = function(jobid, lt)
	return GetValFromTbl(PCImfs, jobid, lt)
end

ReqPCPal = function(jobid, lt)
	return GetValFromTbl(PCPals, jobid, lt)
end

ReqPCHandPath = function(jobid, lt)
	return GetValFromTbl(PCHands, jobid, lt)
end

ReqPCJobName = function(jobid, lt)
	return GetValFromTbl(PCNames, jobid, lt, false, true)
end

-- ============================================================
-- Inheritance Map Functions (fallback lookups)
-- ============================================================

MapPCPath = function(jobid, lt)
	return GetValFromTbl(PCPathInheritTbl, jobid, lt, true)
end

MapPCImf = function(jobid, lt)
	return GetValFromTbl(PCImfInheritTbl, jobid, lt, true)
end

MapPCPal = function(jobid, lt)
	return GetValFromTbl(PCPalInheritTbl, jobid, lt, true)
end

MapPCHandPath = function(jobid, lt)
	return GetValFromTbl(PCHandInheritTbl, jobid, lt, true)
end

MapPCJobName = function(jobid, lt)
	return GetValFromTbl(PCNameInheritTbl, jobid, lt, true, true)
end

-- ============================================================
-- Gender Name Override
-- ============================================================

GetPCNameOvrd = function(jobid, gender, lt)
	local ltKey = lt ~= nil and ("LT_" .. lt) or nil
	local need_lang = (PCNames[ltKey] ~= nil and PCNames[ltKey][jobid] ~= nil)
	local ovrdtbl = (gender == 0 and PCNames_F or PCNames_M)

	local val
	if ovrdtbl[ltKey] ~= nil
	then
		val = ovrdtbl[ltKey][jobid]
	end

	if val == nil and not need_lang
	then
		val = ovrdtbl[jobid]
	end

	if val == nil
	then
		jobid = MapPCJobName(jobid, lt)
		if jobid >= 0
		then
			GetPCNameOvrd(jobid, gender, lt)
		end
	end

	if val ~= nil
	then
		return val
	else
		return ""
	end
end

-- ============================================================
-- Mount / Shrink / Scale Helpers
-- ============================================================

GetHalter = function(jobid)
	return Halter_Table[jobid] or jobid
end

IsDwarf = function(jobid)
	if Shrink_Map[jobid]
	then
		return 1
	else
		return 0
	end
end

GetSprScale = function(jobid)
	local scale = Shrink_Map[jobid]
	if scale == 0 or scale == nil
	then
		return 0
	else
		return tonumber(scale, 16)
	end
end

-- ============================================================
-- Auto-populate PCNames from stock GRF data
-- ============================================================
-- PCJobNameTable is loaded from GRF by stock LoadLuaScripts.
-- This fills PCNames for all standard jobs that don't already
-- have a custom entry, so Phase 9c can display correct names.

if PCJobNameTable and PCNames then
	for id, entry in pairs(PCJobNameTable) do
		if PCNames[id] == nil then
			if type(entry) == "table" then
				PCNames[id] = entry["LT_0"] or entry["LT_1"] or entry[1]
			elseif type(entry) == "string" then
				PCNames[id] = entry
			end
		end
	end
end

-- ============================================================
-- Auto-populate mounted/transcendent variant names from base
-- ============================================================
-- Stock client uses *2 IDs for peco/dragon/mado mounted forms
-- (e.g. LORD_KNIGHT 4008 -> LORD_KNIGHT2 4014). PCJobNameTable
-- from GRF does not include the mounted variants, so display
-- code hits the "Poring" fallback. This pass copies each base
-- name onto its variant(s) when the variant has no entry yet.
-- Source: CMode::GetJobClassID @ 0x00d5b580.

local PC_MOUNT_VARIANTS = {
	[7]      = 13,                                    -- KNIGHT -> KNIGHT2
	[14]     = 21,                                    -- CRUSADER -> CRUSADER2
	[0xFA8]  = 0xFAE,                                 -- LORD_KNIGHT -> LORD_KNIGHT2
	[0xFAF]  = 0xFB6,                                 -- PALADIN -> PALADIN2
	[0xFBE]  = 0xFC4,
	[0xFC5]  = 0xFCC,
	[0xFCF]  = 0xFD0,
	[0xFD6]  = { 0xFF0, 0xFF8, 0xFFA, 0xFFC, 0xFFE }, -- Rune Knight dragon variants
	[0xFD8]  = 0xFF4,
	[0xFDA]  = 0xFF6,
	[0xFDC]  = { 0xFF1, 0xFF9, 0xFFB, 0xFFD, 0xFFF }, -- Rune Knight (trans) dragons
	[0xFDE]  = 0xFF5,
	[0xFE0]  = 0xFF7,
	[0xFE2]  = 0xFF2,
	[0xFE9]  = 0xFF3,
	[0x1000] = 0x100D,
	[0x1002] = 0x100F,
	[0x1004] = 0x1010,
	[0x1006] = 0x100E,
	[0x1082] = 0x108E,
	[0x108F] = 0x1093,
	[0x1091] = 0x1094,
	[0x109C] = 0x10B8,
	[0x109D] = 0x10B7,
	[0x10A1] = 0x10B6,
	[0x10A2] = 0x10B9,
	[0x10CE] = 0x10DC,
}

if PCNames then
	for base, variants in pairs(PC_MOUNT_VARIANTS) do
		local baseName = PCNames[base]
		if baseName ~= nil then
			if type(variants) == "table" then
				for _, v in ipairs(variants) do
					if PCNames[v] == nil then
						PCNames[v] = baseName
					end
				end
			elseif PCNames[variants] == nil then
				PCNames[variants] = baseName
			end
		end
	end
end

-- Skill tree tier override for multi-tier custom jobs
-- Wraps InitSkillTreeView to set correct tier for custom job chains
if InitSkillTreeView then
    local _origISTV = InitSkillTreeView
    InitSkillTreeView = function(jobId, tier)
        if JOB_SKILL_TIER and JOB_SKILL_TIER[jobId] then
            tier = JOB_SKILL_TIER[jobId]
        end
        return _origISTV(jobId, tier)
    end
end
