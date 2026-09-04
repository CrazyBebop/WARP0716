--[[
  CustomJobs Lua Data
  Author: CrazyBebop
  Last Modified: 2026-03-16
]]--

-- ============================================================
-- Custom Job IDs
-- ============================================================
-- Stock job IDs are auto-populated by the do-block below, so you can
-- write `PCNames[PCIds.LORD_KNIGHT2] = "Lord Tite"` (or
-- `PCNames[4014] = "Lord Tite"` - both forms work) in PCNames.lua.
--
-- Add YOUR custom job IDs after the "ADD CUSTOM JOBS BELOW" marker.
--
-- Example:
--   PCIds.MY_CUSTOM_JOB = 4500
-- ============================================================

PCIds = PCIds or {}

-- ============================================================
-- Stock job IDs (auto-populated - do not edit this block)
-- ============================================================
-- Aliases provided for both rAthena (LORD_KNIGHT2) and legacy WARP
-- (LORD_MOUNT) mounted-variant naming, plus rAthena (_T) and legacy
-- (_H) transcendent naming. Pre-define an entry before this block to
-- override the default.
do
	local stock = {
		-- 1st classes
		NOVICE   = 0,    SWORDMAN  = 1,   MAGICIAN  = 2,   ARCHER    = 3,
		ACOLYTE  = 4,    MERCHANT  = 5,   THIEF     = 6,

		-- 2nd classes
		KNIGHT     = 7,  PRIEST    = 8,   WIZARD    = 9,   BLACKSMITH = 10,
		HUNTER     = 11, ASSASSIN  = 12,
		KNIGHT2    = 13, KNIGHT_MOUNT = 13,         -- Knight on peco
		CRUSADER   = 14, MONK      = 15,  SAGE      = 16,  ROGUE      = 17,
		ALCHEMIST  = 18, BARD      = 19,  DANCER    = 20,
		CRUSADER2  = 21, CRUS_MOUNT = 21,           -- Crusader on peco

		-- Costumes / display states
		MARRIED      = 22, SUPERNOVICE  = 23, GUNSLINGER   = 24, NINJA   = 25,
		SANTA        = 26, SUMMER       = 27, HANBOK       = 28,
		OKTOBERFEST  = 29, SUMMER2      = 30,

		-- Transcendent 1st classes (rAthena _T / legacy _H aliases)
		NOVICE_T   = 4001, NOVICE_H   = 4001,
		SWORDMAN_T = 4002, SWORDMAN_H = 4002,
		MAGICIAN_T = 4003, MAGICIAN_H = 4003,
		ARCHER_T   = 4004, ARCHER_H   = 4004,
		ACOLYTE_T  = 4005, ACOLYTE_H  = 4005,
		MERCHANT_T = 4006, MERCHANT_H = 4006,
		THIEF_T    = 4007, THIEF_H    = 4007,

		-- Transcendent 2nd classes
		LORD_KNIGHT  = 4008, HIGH_PRIEST = 4009, HIGH_WIZARD = 4010,
		WHITESMITH   = 4011, SNIPER      = 4012, ASSASSIN_X  = 4013,
		LORD_KNIGHT2 = 4014, LORD_MOUNT  = 4014,         -- Lord Knight on peco
		PALADIN      = 4015, CHAMPION    = 4016, PROFESSOR   = 4017,
		STALKER      = 4018, CREATOR     = 4019, CLOWN       = 4020,
		GYPSY        = 4021,
		PALADIN2     = 4022, PAL_MOUNT   = 4022,         -- Paladin on peco

		-- Baby 1st classes
		NOVICE_B   = 4023, SWORDMAN_B = 4024, MAGICIAN_B = 4025,
		ARCHER_B   = 4026, ACOLYTE_B  = 4027, MERCHANT_B = 4028,
		THIEF_B    = 4029,

		-- Baby 2nd classes
		KNIGHT_B    = 4030, PRIEST_B    = 4031, WIZARD_B   = 4032,
		BLACKSMITH_B = 4033, HUNTER_B   = 4034, ASSASSIN_B = 4035,
		KNIGHT_B2   = 4036, KNIGHT_MOUNT_B = 4036,
		CRUSADER_B  = 4037, MONK_B      = 4038, SAGE_B     = 4039,
		ROGUE_B     = 4040, ALCHEMIST_B = 4041, BARD_B     = 4042,
		DANCER_B    = 4043,
		CRUSADER_B2 = 4044, CRUS_MOUNT_B = 4044,

		SUPERNOVICE_B  = 4045,
		TAEKWON        = 4046,
		STAR_GLADIATOR = 4047, STAR_GLAD = 4047,
		STAR_GLAD_F    = 4048,                          -- Union mode (flying)
		SOUL_LINKER    = 4049,

		-- "Unused" classes
		GANGSI         = 4050,
		DEATH_KNIGHT   = 4051, DEATHKNIGHT = 4051,
		DARK_COLLECTOR = 4052, COLLECTOR   = 4052,

		-- 3rd classes
		RUNE_KNIGHT  = 4054, WARLOCK     = 4055, RANGER       = 4056,
		ARCHBISHOP   = 4057, MECHANIC    = 4058, GUILLOTINE_X = 4059,
		-- Trans 3rd
		RUNE_KNIGHT_T  = 4060, RUNE_KNIGHT_H  = 4060,
		WARLOCK_T      = 4061, WARLOCK_H      = 4061,
		RANGER_T       = 4062, RANGER_H       = 4062,
		ARCHBISHOP_T   = 4063, ARCHBISHOP_H   = 4063,
		MECHANIC_T     = 4064, MECHANIC_H     = 4064,
		GUILLOTINE_X_T = 4065, GUILLOTINE_X_H = 4065,

		ROYAL_GUARD   = 4066, SORCERER  = 4067, MINSTREL  = 4068,
		WANDERER      = 4069, SURA      = 4070, GENETIC   = 4071,
		SHADOW_CHASER = 4072,
		ROYAL_GUARD_T   = 4073, ROYAL_GUARD_H   = 4073,
		SORCERER_T      = 4074, SORCERER_H      = 4074,
		MINSTREL_T      = 4075, MINSTREL_H      = 4075,
		WANDERER_T      = 4076, WANDERER_H      = 4076,
		SURA_T          = 4077, SURA_H          = 4077,
		GENETIC_T       = 4078, GENETIC_H       = 4078,
		SHADOW_CHASER_T = 4079, SHADOW_CHASER_H = 4079,

		-- 3rd-class mounts (rAthena *2 / legacy *_MOUNT aliases)
		RUNE_KNIGHT2   = 4080, RUNE_MOUNT     = 4080,    -- Rune Knight green dragon
		RUNE_KNIGHT_T2 = 4081, RUNE_MOUNT_H   = 4081,
		ROYAL_GUARD2   = 4082, ROYAL_MOUNT    = 4082,    -- Royal Guard gryphon
		ROYAL_GUARD_T2 = 4083, ROYAL_MOUNT_H  = 4083,
		RANGER2        = 4084, RANGER_MOUNT   = 4084,    -- Ranger wolf
		RANGER_T2      = 4085, RANGER_MOUNT_H = 4085,
		MECHANIC2      = 4086, MADOGEAR       = 4086,    -- Mechanic mado
		MECHANIC_T2    = 4087, MADOGEAR_H     = 4087,

		-- Rune Knight extra dragon colors
		RUNE_KNIGHT3   = 4088, RUNE_MOUNT2    = 4088,
		RUNE_KNIGHT_T3 = 4089, RUNE_MOUNT2_H  = 4089,
		RUNE_KNIGHT4   = 4090, RUNE_MOUNT3    = 4090,
		RUNE_KNIGHT_T4 = 4091, RUNE_MOUNT3_H  = 4091,
		RUNE_KNIGHT5   = 4092, RUNE_MOUNT4    = 4092,
		RUNE_KNIGHT_T5 = 4093, RUNE_MOUNT4_H  = 4093,
		RUNE_KNIGHT6   = 4094, RUNE_MOUNT5    = 4094,
		RUNE_KNIGHT_T6 = 4095, RUNE_MOUNT5_H  = 4095,

		-- Baby 3rd classes
		RUNE_KNIGHT_B   = 4096, WARLOCK_B   = 4097, RANGER_B       = 4098,
		ARCHBISHOP_B    = 4099, MECHANIC_B  = 4100, GUILLOTINE_X_B = 4101,
		ROYAL_GUARD_B   = 4102, SORCERER_B  = 4103, MINSTREL_B     = 4104,
		WANDERER_B      = 4105, SURA_B      = 4106, GENETIC_B      = 4107,
		SHADOW_CHASER_B = 4108,
		-- Baby 3rd mounts
		RUNE_KNIGHT_B2  = 4109, RUNE_MOUNT_B   = 4109,
		ROYAL_GUARD_B2  = 4110, ROYAL_MOUNT_B  = 4110,
		RANGER_B2       = 4111, RANGER_MOUNT_B = 4111,
		MECHANIC_B2     = 4112, MADOGEAR_B     = 4112,

		-- Extended classes
		SUPERNOVICE2   = 4190, SUPERNOVICE2_B = 4191,
		KAGEROU        = 4211, OBORO          = 4212,
		REBELLION      = 4215,
		SUMMONER       = 4218,                            -- Doram
		SUMMONER_B     = 4220,
		NINJA_B        = 4222,
		KAGEROU_B      = 4223, OBORO_B          = 4224,
		TAEKWON_B      = 4225,
		STAR_GLAD_B    = 4226, SOUL_LINKER_B    = 4227,
		GUNSLINGER_B   = 4228,
		REBELLION_B    = 4229,

		-- Extended 3rd
		STAR_EMPEROR   = 4239, SOUL_REAPER      = 4240,
		STAR_EMPEROR_B = 4241, SOUL_REAPER_B    = 4242,
		STAR_EMPEROR_F = 4243, STAR_EMPEROR_F_B = 4244,
		SHINKIRO       = 4304, SHIRANUI         = 4305,
		NIGHT_WATCH    = 4306,
		HYPER_NOVICE   = 4307,
		SPIRIT_HANDLER = 4308,

		-- 4th classes
		DRAGON_KNIGHT  = 4252, MEISTER      = 4253, SHADOW_CROSS  = 4254,
		ARCH_MAGE      = 4255, CARDINAL     = 4256, WINDHAWK      = 4257,
		IMPERIAL_GUARD = 4258, BIOLO        = 4259, ABYSS_CHASER  = 4260,
		ELEMENT_MASTER = 4261, INQUISITOR   = 4262, TROUBADOUR    = 4263,
		TROUVERE       = 4264,

		-- 4th-class mounts (rAthena *2 / legacy *_MOUNT aliases)
		WINDHAWK2       = 4278, WINDHAWK_MOUNT = 4278,    -- Windhawk wolf
		MEISTER2        = 4279, MEISTER_MADO   = 4279,    -- Meister mado
		DRAGON_KNIGHT2  = 4280, DRAGON_MOUNT   = 4280,    -- Dragon Knight dragon
		IMPERIAL_GUARD2 = 4281, IMPERIAL_MOUNT = 4281,    -- Imperial Guard peco

		-- Extended 4th
		SKY_EMPEROR    = 4302, SKY_EMPEROR_F = 4316,
		SOUL_ASCETIC   = 4303,
	}
	for k, v in pairs(stock) do
		if PCIds[k] == nil then PCIds[k] = v end
	end
end

-- ====== ADD YOUR CUSTOM JOB IDs BELOW ======
PCIds.EXAMPLE_JOB = 4435
PCIds.EXAMPLE_JOB_B = 4436  -- Baby variant

-- Baby class sprite scaling (shrinks baby jobs to 0.75x)
Scales = Scales or { "3F400000", "3F51EB85", "3F4CCCCD" }
Shrink_Map = Shrink_Map or {}
Shrink_Map[PCIds.EXAMPLE_JOB_B] = Scales[1]
