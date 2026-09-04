--[[
****************************************************************************
*                                                                          *
*   Copyright (C) 2021-2022 Neo-Mind                                       *
*                                                                          *
*   This file is a part of WARP project (specific to RO clients)           *
*                                                                          *
*   WARP is free software: you can redistribute it and/or modify           *
*   it under the terms of the GNU General Public License as published by   *
*   the Free Software Foundation, either version 3 of the License, or      *
*   (at your option) any later version.                                    *
*                                                                          *
*   This program is distributed in the hope that it will be useful,        *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
*   GNU General Public License for more details.                           *
*                                                                          *
*   You should have received a copy of the GNU General Public License      *
*   along with this program.  If not, see <http://www.gnu.org/licenses/>.  *
*                                                                          *
*                                                                          *
|**************************************************************************|
*                                                                          *
*   Author(s)     : Neo-Mind                                               *
*   Created Date  : 2021-03-21                                             *
*   Last Modified : 2021-08-23                                             *
*                                                                          *
****************************************************************************
]]--

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯·´¯)
( \                                                / )
 ( ) Default set of prefixes used for job sprites ( )
  (/                                              \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.)

]]--

PCPaths =
{
	--[[
	    _   ___   ___     ___  ___   ___
	 _ | | / _ \ | _ )   |_ _||   \ / __|
	| || || (_) || _ \    | | | |) |\__ \
	 \__/  \___/ |___/   |___||___/ |___/

	]]--

	-----------------
	-- 1st Classes --
	-----------------
	[PCIds.NOVICE]   = "ÃÊº¸ÀÚ",
	[PCIds.SWORDMAN] = "°Ë»ç",
	[PCIds.MAGICIAN] = "¸¶¹ý»ç",
	[PCIds.ARCHER]   = "±Ã¼ö",
	[PCIds.ACOLYTE]  = "¼ºÁ÷ÀÚ",
	[PCIds.MERCHANT] = "»óÀÎ",
	[PCIds.THIEF]    = "µµµÏ",

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCIds.SUPERNOVICE]  = "½´ÆÛ³ëºñ½º",
	[PCIds.GUNSLINGER]   = "°Ç³Ê",
	[PCIds.NINJA]        = "´ÑÀÚ",
	[PCIds.TAEKWON]      = "ÅÂ±Ç¼Ò³â",

	-----------------
	-- 2nd Classes --
	-----------------
	[PCIds.KNIGHT]       = "±â»ç",
	[PCIds.KNIGHT_MOUNT] = "ÆäÄÚÆäÄÚ_±â»ç",
	[PCIds.PRIEST]       = "ÇÁ¸®½ºÆ®",
	[PCIds.WIZARD]       = "À§Àúµå",
	[PCIds.BLACKSMITH]   = "Á¦Ã¶°ø",
	[PCIds.HUNTER]       = "ÇåÅÍ",
	[PCIds.ASSASSIN]     = "¾î¼¼½Å",

	[PCIds.CRUSADER]     = "Å©·ç¼¼ÀÌ´õ",
	[PCIds.CRUS_MOUNT]   = "½ÅÆäÄÚÅ©·ç¼¼ÀÌ´õ",
	[PCIds.MONK]         = "¸ùÅ©",
	[PCIds.SAGE]         = "¼¼ÀÌÁö",
	[PCIds.ROGUE]        = "·Î±×",
	[PCIds.ALCHEMIST]    = "¿¬±Ý¼ú»ç",
	[PCIds.BARD]         = "¹Ùµå",
	[PCIds.DANCER]       = "¹«Èñ",

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCIds.LORD_KNIGHT] = "·Îµå³ªÀÌÆ®",
	[PCIds.LORD_MOUNT]  = "·ÎµåÆäÄÚ", --Peco mount for Lord Knight
	[PCIds.HIGH_PRIEST] = "ÇÏÀÌÇÁ¸®",
	[PCIds.HIGH_WIZARD] = "ÇÏÀÌÀ§Àúµå",
	[PCIds.WHITESMITH]  = "È­ÀÌÆ®½º¹Ì½º",
	[PCIds.SNIPER]      = "½º³ªÀÌÆÛ",
	[PCIds.ASSASSIN_X]  = "¾î½Ø½ÅÅ©·Î½º",

	[PCIds.PALADIN]     = "ÆÈ¶óµò",
	[PCIds.PAL_MOUNT]   = "ÆäÄÚÆÈ¶óµò", --Peco mount for Paladin
	[PCIds.CHAMPION]    = "Ã¨ÇÇ¿Â",
	[PCIds.PROFESSOR]   = "ÇÁ·ÎÆä¼­",
	[PCIds.STALKER]     = "½ºÅäÄ¿",
	[PCIds.CREATOR]     = "Å©¸®¿¡ÀÌÅÍ",
	[PCIds.CLOWN]       = "Å¬¶ó¿î",
	[PCIds.GYPSY]       = "Áý½Ã",

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCIds.HYPER_NOVICE] = "HYPER_NOVICE",
	[PCIds.REBELLION]    = "rebellion" ,
	[PCIds.KAGEROU]      = "kagerou",
	[PCIds.OBORO]        = "oboro",
	[PCIds.STAR_GLAD]    = "±Ç¼º",
	[PCIds.STAR_GLAD_F]  = "±Ç¼ºÀ¶ÇÕ",
	[PCIds.SOUL_LINKER]  = "¼Ò¿ï¸µÄ¿",


	--------------------
	-- Custom Classes --
	--------------------

	-----------------
	-- 3rd Classes --
	-----------------
	[PCIds.RUNE_KNIGHT]    = "·é³ªÀÌÆ®",
	[PCIds.RUNE_MOUNT]     = "·é³ªÀÌÆ®»Ú¶ì",
	[PCIds.RUNE_MOUNT2]    = "·é³ªÀÌÆ®»Ú¶ì2",
	[PCIds.RUNE_MOUNT3]    = "·é³ªÀÌÆ®»Ú¶ì3",
	[PCIds.RUNE_MOUNT4]    = "·é³ªÀÌÆ®»Ú¶ì4",
	[PCIds.RUNE_MOUNT5]    = "·é³ªÀÌÆ®»Ú¶ì5",
	[PCIds.WARLOCK]        = "¿ö·Ï",
	[PCIds.RANGER]         = "·¹ÀÎÁ®",
	[PCIds.RANGER_MOUNT]   = "·¹ÀÎÁ®´Á´ë",
	[PCIds.ARCHBISHOP]     = "¾ÆÅ©ºñ¼ó",
	[PCIds.MECHANIC]       = "¹ÌÄÉ´Ð",
	[PCIds.MADOGEAR]       = "¸¶µµ±â¾î",
	[PCIds.GUILLOTINE_X]   = "±æ·ÎÆ¾Å©·Î½º",

	[PCIds.ROYAL_GUARD]    = "°¡µå",
	[PCIds.ROYAL_MOUNT]    = "±×¸®Æù°¡µå",
	[PCIds.SORCERER]       = "¼Ò¼­·¯",
	[PCIds.MINSTREL]       = "¹Î½ºÆ®·²",
	[PCIds.WANDERER]       = "¿ø´õ·¯",
	[PCIds.SURA]           = "½´¶ó",
	[PCIds.GENETIC]        = "Á¦³×¸¯",
	[PCIds.SHADOW_CHASER]  = "½¦µµ¿ìÃ¼ÀÌ¼­",

	--------------------------
	-- Extended 3rd Classes --
	--------------------------
	[PCIds.NIGHT_WATCH]    = "NIGHT_WATCH",
	[PCIds.SHINKIRO]       = "SHINKIRO",
	[PCIds.SHIRANUI]       = "SHIRANUI",
	[PCIds.STAR_EMPEROR]   = "¼ºÁ¦",
	[PCIds.STAR_EMPEROR_F] = "¼ºÁ¦À¶ÇÕ",
	[PCIds.SOUL_REAPER]    = "¼Ò¿ï¸®ÆÛ",

	-----------------
	-- 4th Classes --
	-----------------
	[PCIds.DRAGON_KNIGHT]   = "DRAGON_KNIGHT",
	[PCIds.DRAGON_MOUNT]    = "DRAGON_KNIGHT_CHICKEN",
	[PCIds.MEISTER]         = "MEISTER",
	[PCIds.MEISTER_MADO]    = "MEISTER_MADOGEAR1",
	[PCIds.SHADOW_CROSS]    = "SHADOW_CROSS",
	[PCIds.ARCH_MAGE]       = "ARCH_MAGE",
	[PCIds.CARDINAL]        = "CARDINAL",
	[PCIds.WINDHAWK]        = "WINDHAWK",
	[PCIds.WINDHAWK_MOUNT]  = "WOLF_WINDHAWK", --Wolf mount for Windhawk

	[PCIds.IMPERIAL_GUARD]  = "IMPERIAL_GUARD",
	[PCIds.IMPERIAL_MOUNT]  = "IMPERIAL_GUARD_CHICKEN",
	[PCIds.BIOLO]           = "BIOLO",
	[PCIds.ABYSS_CHASER]    = "ABYSS_CHASER",
	[PCIds.ELEMENT_MASTER]  = "ELEMETAL_MASTER",
	[PCIds.INQUISITOR]      = "INQUISITOR",
	[PCIds.TROUBADOUR]      = "TROUBADOUR",
	[PCIds.TROUVERE]        = "TROUVERE",

	--------------------------
	-- Extended 4th Classes --
	--------------------------
	[PCIds.SKY_EMPEROR]   = "SKY_EMPEROR",
	[PCIds.SKY_EMPEROR_F] = "SKY_EMPEROR2",
	[PCIds.SOUL_ASCETIC]  = "SOUL_ASCETIC",

	--------------
	-- Costumes --
	--------------
	[PCIds.MARRIED]      = "°áÈ¥",
	[PCIds.SANTA]        = "»êÅ¸",
	[PCIds.SUMMER]       = "¿©¸§",
	[PCIds.HANBOK]       = "ÇÑº¹",
	[PCIds.OKTOBERFEST]  = "¿ÁÅä¹öÆÐ½ºÆ®",
	[PCIds.SUMMER2]      = "¿©¸§2",

	-----------------------
	-- Doram 1st Classes --
	-----------------------
	[PCIds.SUMMONER]     = "summoner",

	-----------------------
	-- Doram 2nd Classes --
	-----------------------
	[PCIds.SPIRIT_HANDLER] = "SPIRIT_HANDLER",

	--------------------
	-- Custom Classes --
	--------------------

	--[[
	 __  __   ___   _   _  _  _  _____     ___  ___   ___
	|  \/  | / _ \ | | | || \| ||_   _|   |_ _||   \ / __|
	| |\/| || (_) || |_| || .  |  | |      | | | |) |\__ \
	|_|  |_| \___/  \___/ |_|\_|  |_|     |___||___/ |___/

	]]--

	-----------------
	-- 1st Classes --
	-----------------
	[PCMounts.PORING_NOVICE]    = "³ëºñ½ºÆ÷¸µ",
	[PCMounts.PECO_SWORD]       = "ÆäÄÚ°Ë»ç",
	[PCMounts.FOX_MAGICIAN]     = "¿©¿ì¸¶¹ý»ç",
	[PCMounts.OSTRICH_ARCHER]   = "Å¸Á¶±Ã¼ö",
	[PCMounts.SHEEP_ACO]        = "º¹»ç¾ËÆÄÄ«",
	[PCMounts.PIG_MERCHANT]     = "»óÀÎ¸äµÅÁö",
	[PCMounts.HYENA_THIEF]      = "ÄÌº£·Î½ºµµµÏ",

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCMounts.PORING_S_NOVICE]  = "½´ÆÛ³ëºñ½ºÆ÷¸µ",
	[PCMounts.BIKE_GUNNER]      = "ÆäÄÚ°Ç³Ê",
	[PCMounts.FROG_NINJA]       = "µÎ²¨ºñ´ÑÀÚ",
	[PCMounts.PORING_TAEKWON]   = "ÅÂ±Ç¼Ò³âÆ÷¸µ",

	-----------------
	-- 2nd Classes --
	-----------------
	[PCMounts.LION_KNIGHT]      = "»çÀÚ±â»ç",
	[PCMounts.SHEEP_PRIEST]     = "ÇÁ¸®½ºÆ®¾ËÆÄÄ«",
	[PCMounts.FOX_WIZARD]       = "¿©¿ìÀ§Àúµå",
	[PCMounts.PIG_BLACKSMITH]   = "Á¦Ã¶°ø¸äµÅÁö",
	[PCMounts.OSTRICH_HUNTER]   = "Å¸Á¶ÇåÅÍ",
	[PCMounts.HYENA_ASSASSIN]   = "ÄÌº£·Î½º¾î½ê½Å",

	[PCMounts.LION_CRUSADER]    = "»çÀÚÅ©·ç¼¼ÀÌ´õ",
	[PCMounts.SHEEP_MONK]       = "¸ùÅ©¾ËÆÄÄ«",
	[PCMounts.FOX_SAGE]         = "¿©¿ì¼¼ÀÌÁö",
	[PCMounts.HYENA_ROGUE]      = "ÄÌº£·Î½º·Î±×",
	[PCMounts.PIG_ALCHE]        = "¿¬±Ý¼ú»ç¸äµÅÁö",
	[PCMounts.OSTRICH_BARD]     = "Å¸Á¶¹Ùµå",
	[PCMounts.OSTRICH_DANCER]   = "Å¸Á¶¹«Èñ",

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCMounts.LION_LORD_KNIGHT] = "»çÀÚ·Îµå³ªÀÌÆ®",
	[PCMounts.SHEEP_HI_PRIEST]  = "ÇÏÀÌÇÁ¸®½ºÆ®¾ËÆÄÄ«",
	[PCMounts.FOX_HI_WIZ]       = "¿©¿ìÇÏÀÌÀ§Àúµå",
	[PCMounts.PIG_WHITESMITH]   = "È­ÀÌÆ®½º¹Ì½º¸äµÅÁö",
	[PCMounts.OSTRICH_SNIPER]   = "Å¸Á¶½º³ªÀÌÆÛ",
	[PCMounts.HYENA_SIN_X]      = "ÄÌº£·Î½º¾î½ê½ÅÅ©·Î½º",

	[PCMounts.LION_PALADIN]     = "»çÀÚÆÈ¶óµò",
	[PCMounts.SHEEP_CHAMP]      = "Ã¨ÇÇ¿Â¾ËÆÄÄ«",
	[PCMounts.FOX_PROF]         = "¿©¿ìÇÁ·ÎÆä¼­",
	[PCMounts.HYENA_STALKER]    = "ÄÌº£·Î½º½ºÅäÄ¿",
	[PCMounts.PIG_CREATOR]      = "Å©¸®¿¡ÀÌÅÍ¸äµÅÁö",
	[PCMounts.OSTRICH_CLOWN]    = "Å¸Á¶Å©¶ó¿î",
	[PCMounts.OSTRICH_GYPSY]    = "Å¸Á¶Â¤½Ã",

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCMounts.PORING_H_NOVICE]  = "HYPER_NOVICE_RIDING",
	[PCMounts.BIKE_REBELLION]   = "peco_rebellion",
	[PCMounts.FROG_KAGEROU]     = "frog_kagerou",
	[PCMounts.FROG_OBORO]       = "frog_oboro",
	[PCMounts.PORING_STAR]      = "±Ç¼ºÆ÷¸µ",
	[PCMounts.FROG_LINKER]      = "µÎ²¨ºñ¼Ò¿ï¸µÄ¿",

	--------------------------------------------------
	-- 3rd Classes (Transcendent also use the same) --
	--------------------------------------------------
	[PCMounts.LION_RUNE_KNIGHT]  = "»çÀÚ·é³ªÀÌÆ®",
	[PCMounts.FOX_WARLOCK]       = "¿©¿ì¿ö·Ï",
	[PCMounts.OSTRICH_RANGER]    = "Å¸Á¶·¹ÀÎÁ®",
	[PCMounts.SHEEP_BISHOP]      = "¾ÆÅ©ºñ¼ó¾ËÆÄÄ«",
	[PCMounts.PIG_MECHANIC]      = "¹ÌÄÉ´Ð¸äµÅÁö",
	[PCMounts.HYENA_G_CROSS]     = "ÄÌº£·Î½º±æ·ÎÆ¾Å©·Î½º",

	[PCMounts.LION_ROYAL_GUARD]  = "»çÀÚ·Î¾â°¡µå",
	[PCMounts.FOX_SORCERER]      = "¿©¿ì¼Ò¼­·¯",
	[PCMounts.OSTRICH_MINSTREL]  = "Å¸Á¶¹Î½ºÆ®·²",
	[PCMounts.OSTRICH_WANDERER]  = "Å¸Á¶¿ø´õ·¯",
	[PCMounts.SHEEP_SURA]        = "½´¶ó¾ËÆÄÄ«",
	[PCMounts.PIG_GENETIC]       = "Á¦³×¸¯¸äµÅÁö",
	[PCMounts.HYENA_S_CHASER]    = "ÄÌº£·Î½º½¦µµ¿ìÃ¼ÀÌ¼­",

	--------------------------
	-- Extended 3rd Classes --
	--------------------------
	[PCMounts.BIKE_NIGHT_WATCH]      = "NIGHT_WATCH_RIDING",
	[PCMounts.FROG_SHINKIRO]         = "SHINKIRO_RIDING",
	[PCMounts.FROG_SHIRANUI]         = "SHIRANUI_RIDING",
	[PCMounts.HAETAE_STAR_EMPEROR]   = "ÇØÅÂ¼ºÁ¦",
	[PCMounts.HAETAE_SOUL_REAPER]    = "ÇØÅÂ¼Ò¿ï¸®ÆÛ",

	-----------------
	-- 4th Classes --
	-----------------
	[PCMounts.LION_DRAGON_KNIGHT]   = "DRAGON_KNIGHT_RIDING",
	[PCMounts.PIG_MEISTER]          = "MEISTER_RIDING",
	[PCMounts.HYENA_SHADOW_CROSS]   = "SHADOW_CROSS_RIDING",
	[PCMounts.FOX_ARCH_MAGE]        = "ARCH_MAGE_RIDING",
	[PCMounts.SHEEP_CARDINAL]       = "CARDINAL_RIDING",
	[PCMounts.OSTRICH_WINDHAWK]     = "WINDHAWK_RIDING",

	[PCMounts.LION_IMPERIAL_GUARD]  = "IMPERIAL_GUARD_RIDING",
	[PCMounts.PIG_BIOLO]            = "BIOLO_RIDING",
	[PCMounts.HYENA_ABYSS_CHASER]   = "ABYSS_CHASER_RIDING",
	[PCMounts.FOX_ELEMENT_MASTER]   = "ELEMETAL_MASTER_RIDING",
	[PCMounts.SHEEP_INQUISITOR]     = "INQUISITOR_RIDING",
	[PCMounts.OSTRICH_TROUBADOUR]   = "TROUBADOUR_RIDING",
	[PCMounts.OSTRICH_TROUVERE]     = "TROUVERE_RIDING",

	--------------------------
	-- Extended 4th Classes --
	--------------------------
	[PCMounts.HAETAE_SKY_EMPEROR]   = "SKY_EMPEROR_RIDING",
	[PCMounts.HAETAE_SOUL_ASCETIC]  = "SOUL_ASCETIC_RIDING",

	-----------------------
	-- Doram 1st Classes --
	-----------------------
	[PCMounts.SUMM_MOUNT]           = "cart_summoner",

	-----------------------
	-- Doram 2nd Classes --
	-----------------------
	[PCMounts.SP_HANDLER_MOUNT]     = "SPIRIT_HANDLER_RIDING",	
}

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯)
( \                                                      / )
 ( ) Inheritance table for mapping ids with same prefix ( )
  (/                                                    \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.)

]]--

PCPathInheritTbl =
{
	--[[
	    _   ___   ___     ___  ___   ___
	 _ | | / _ \ | _ )   |_ _||   \ / __|
	| || || (_) || _ \    | | | |) |\__ \
	 \__/  \___/ |___/   |___||___/ |___/

	]]--

	----------------------
	-- Baby 1st Classes --
	----------------------
	[PCIds.NOVICE_B]   = PCIds.NOVICE,
	[PCIds.SWORDMAN_B] = PCIds.SWORDMAN,
	[PCIds.MAGICIAN_B] = PCIds.MAGICIAN,
	[PCIds.ARCHER_B]   = PCIds.ARCHER,
	[PCIds.ACOLYTE_B]  = PCIds.ACOLYTE,
	[PCIds.MERCHANT_B] = PCIds.MERCHANT,
	[PCIds.THIEF_B]    = PCIds.THIEF,

	------------------------------
	-- Transcendent 1st Classes --
	------------------------------
	[PCIds.NOVICE_H]   = PCIds.NOVICE,
	[PCIds.SWORDMAN_H] = PCIds.SWORDMAN,
	[PCIds.MAGICIAN_H] = PCIds.MAGICIAN,
	[PCIds.ARCHER_H]   = PCIds.ARCHER,
	[PCIds.ACOLYTE_H]  = PCIds.ACOLYTE,
	[PCIds.MERCHANT_H] = PCIds.MERCHANT,
	[PCIds.THIEF_H]    = PCIds.THIEF,

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCIds.SUPERNOVICE2] = PCIds.SUPERNOVICE,

	-------------------------------
	-- Baby Extended 1st Classes --
	-------------------------------
	[PCIds.SUPERNOVICE_B]  = PCIds.SUPERNOVICE,
	[PCIds.SUPERNOVICE2_B] = PCIds.SUPERNOVICE,
	[PCIds.GUNSLINGER_B]   = PCIds.GUNSLINGER,
	[PCIds.NINJA_B]        = PCIds.NINJA,
	[PCIds.TAEKWON_B]      = PCIds.TAEKWON,

	----------------------
	-- Baby 2nd Classes --
	----------------------
	[PCIds.KNIGHT_B]       = PCIds.KNIGHT,
	[PCIds.KNIGHT_MOUNT_B] = PCIds.KNIGHT_MOUNT,
	[PCIds.PRIEST_B]       = PCIds.PRIEST,
	[PCIds.WIZARD_B]       = PCIds.WIZARD,
	[PCIds.BLACKSMITH_B]   = PCIds.BLACKSMITH,
	[PCIds.HUNTER_B]       = PCIds.HUNTER,
	[PCIds.ASSASSIN_B]     = PCIds.ASSASSIN,

	[PCIds.CRUSADER_B]     = PCIds.CRUSADER,
	[PCIds.CRUS_MOUNT_B]   = PCIds.CRUS_MOUNT,
	[PCIds.MONK_B]         = PCIds.MONK,
	[PCIds.SAGE_B]         = PCIds.SAGE,
	[PCIds.ROGUE_B]        = PCIds.ROGUE,
	[PCIds.ALCHEMIST_B]    = PCIds.ALCHEMIST,
	[PCIds.BARD_B]         = PCIds.BARD,
	[PCIds.DANCER_B]       = PCIds.DANCER,

	-------------------------------
	-- Baby Extended 2nd Classes --
	-------------------------------
	[PCIds.REBELLION_B]    = PCIds.REBELLION,
	[PCIds.KAGEROU_B]      = PCIds.KAGEROU,
	[PCIds.OBORO_B]        = PCIds.OBORO,
	[PCIds.STAR_GLAD_B]    = PCIds.STAR_GLAD,
	[PCIds.STAR_GLAD_F_B]  = PCIds.STAR_GLAD_F,
	[PCIds.SOUL_LINKER_B]  = PCIds.SOUL_LINKER,

	----------------------
	-- Baby 3rd Classes --
	----------------------
	[PCIds.RUNE_KNIGHT_B]   = PCIds.RUNE_KNIGHT,
	[PCIds.RUNE_MOUNT_B]    = PCIds.RUNE_MOUNT,
	[PCIds.WARLOCK_B]       = PCIds.WARLOCK,
	[PCIds.RANGER_B]        = PCIds.RANGER,
	[PCIds.RANGER_MOUNT_B]  = PCIds.RANGER_MOUNT,
	[PCIds.ARCHBISHOP_B]    = PCIds.ARCHBISHOP,
	[PCIds.MECHANIC_B]      = PCIds.MECHANIC,
	[PCIds.MADOGEAR_B]      = PCIds.MADOGEAR,
	[PCIds.GUILLOTINE_X_B]  = PCIds.GUILLOTINE_X,

	[PCIds.ROYAL_GUARD_B]   = PCIds.ROYAL_GUARD,
	[PCIds.ROYAL_MOUNT_B]   = PCIds.ROYAL_MOUNT,
	[PCIds.SORCERER_B]      = PCIds.SORCERER,
	[PCIds.MINSTREL_B]      = PCIds.MINSTREL,
	[PCIds.WANDERER_B]      = PCIds.WANDERER,
	[PCIds.SURA_B]          = PCIds.SURA,
	[PCIds.GENETIC_B]       = PCIds.GENETIC,
	[PCIds.SHADOW_CHASER_B] = PCIds.SHADOW_CHASER,

	------------------------------
	-- Transcendent 3rd Classes --
	------------------------------
	[PCIds.RUNE_KNIGHT_H]   = PCIds.RUNE_KNIGHT,
	[PCIds.RUNE_MOUNT_H]    = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT2_H]   = PCIds.RUNE_MOUNT2,
	[PCIds.RUNE_MOUNT3_H]   = PCIds.RUNE_MOUNT3,
	[PCIds.RUNE_MOUNT4_H]   = PCIds.RUNE_MOUNT4,
	[PCIds.RUNE_MOUNT5_H]   = PCIds.RUNE_MOUNT5,
	[PCIds.WARLOCK_H]       = PCIds.WARLOCK,
	[PCIds.RANGER_H]        = PCIds.RANGER,
	[PCIds.RANGER_MOUNT_H]  = PCIds.RANGER_MOUNT,
	[PCIds.ARCHBISHOP_H]    = PCIds.ARCHBISHOP,
	[PCIds.MECHANIC_H]      = PCIds.MECHANIC,
	[PCIds.MADOGEAR_H]      = PCIds.MADOGEAR,
	[PCIds.GUILLOTINE_X_H]  = PCIds.GUILLOTINE_X,

	[PCIds.ROYAL_GUARD_H]   = PCIds.ROYAL_GUARD,
	[PCIds.ROYAL_MOUNT_H]   = PCIds.ROYAL_MOUNT,
	[PCIds.SORCERER_H]      = PCIds.SORCERER,
	[PCIds.MINSTREL_H]      = PCIds.MINSTREL,
	[PCIds.WANDERER_H]      = PCIds.WANDERER,
	[PCIds.SURA_H]          = PCIds.SURA,
	[PCIds.GENETIC_H]       = PCIds.GENETIC,
	[PCIds.SHADOW_CHASER_H] = PCIds.SHADOW_CHASER,

	-------------------------------
	-- Baby Extended 3rd Classes --
	-------------------------------
	[PCIds.STAR_EMPEROR_B]   = PCIds.STAR_EMPEROR,
	[PCIds.STAR_EMPEROR_F_B] = PCIds.STAR_EMPEROR_F,
	[PCIds.SOUL_REAPER_B]    = PCIds.SOUL_REAPER,

	---------------------
	-- Unused classes? --
	---------------------
	[PCIds.GANGSI]      = PCIds.ACOLYTE,
	[PCIds.DEATHKNIGHT] = PCIds.KNIGHT,
	[PCIds.COLLECTOR]   = PCIds.SAGE,

	------------------------
	-- Baby Doram Classes --
	------------------------
	[PCIds.SUMMONER_B]   = PCIds.SUMMONER,

	--[[
	 __  __   ___   _   _  _  _  _____     ___  ___   ___
	|  \/  | / _ \ | | | || \| ||_   _|   |_ _||   \ / __|
	| |\/| || (_) || |_| || .  |  | |      | | | |) |\__ \
	|_|  |_| \___/  \___/ |_|\_|  |_|     |___||___/ |___/

	]]--

	----------------------
	-- Baby 1st Classes --
	----------------------
	[PCMounts.PORING_NOVICE_B]  = PCMounts.PORING_NOVICE,
	[PCMounts.PECO_SWORD_B]     = PCMounts.PECO_SWORD,
	[PCMounts.FOX_MAGICIAN_B]   = PCMounts.FOX_MAGICIAN,
	[PCMounts.OSTRICH_ARCHER_B] = PCMounts.OSTRICH_ARCHER,
	[PCMounts.SHEEP_ACO_B]      = PCMounts.SHEEP_ACO,
	[PCMounts.PIG_MERCHANT_B]   = PCMounts.PIG_MERCHANT,
	[PCMounts.HYENA_THIEF_B]    = PCMounts.HYENA_THIEF,

	------------------------------
	-- Transcendent 1st Classes --
	------------------------------
	[PCMounts.PORING_NOVICE_H]  = PCMounts.PORING_NOVICE,
	[PCMounts.PECO_SWORD_H]     = PCMounts.PECO_SWORD,
	[PCMounts.FOX_MAGICIAN_H]   = PCMounts.FOX_MAGICIAN,
	[PCMounts.OSTRICH_ARCHER_H] = PCMounts.OSTRICH_ARCHER,
	[PCMounts.SHEEP_ACO_H]      = PCMounts.SHEEP_ACO,
	[PCMounts.PIG_MERCHANT_H]   = PCMounts.PIG_MERCHANT,
	[PCMounts.HYENA_THIEF_H]    = PCMounts.HYENA_THIEF,

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCMounts.PORING_S_NOVICE2]   = PCMounts.PORING_S_NOVICE,

	-------------------------------
	-- Baby Extended 1st Classes --
	-------------------------------
	[PCMounts.PORING_S_NOVICE_B]  = PCMounts.PORING_S_NOVICE,
	[PCMounts.PORING_S_NOVICE2_B] = PCMounts.PORING_S_NOVICE,
	[PCMounts.BIKE_GUNNER_B]      = PCMounts.BIKE_GUNNER,
	[PCMounts.FROG_NINJA_B]       = PCMounts.FROG_NINJA,
	[PCMounts.PORING_TAEKWON_B]   = PCMounts.PORING_TAEKWON,

	----------------------
	-- Baby 2nd Classes --
	----------------------
	[PCMounts.LION_KNIGHT_B]    = PCMounts.LION_KNIGHT,
	[PCMounts.SHEEP_PRIEST_B]   = PCMounts.SHEEP_PRIEST,
	[PCMounts.FOX_WIZARD_B]     = PCMounts.FOX_WIZARD,
	[PCMounts.PIG_BLACKSMITH_B] = PCMounts.PIG_BLACKSMITH,
	[PCMounts.OSTRICH_HUNTER_B] = PCMounts.OSTRICH_HUNTER,
	[PCMounts.HYENA_ASSASSIN_B] = PCMounts.HYENA_ASSASSIN,

	[PCMounts.LION_CRUSADER_B]  = PCMounts.LION_CRUSADER,
	[PCMounts.SHEEP_MONK_B]     = PCMounts.SHEEP_MONK,
	[PCMounts.FOX_SAGE_B]       = PCMounts.FOX_SAGE,
	[PCMounts.HYENA_ROGUE_B]    = PCMounts.HYENA_ROGUE,
	[PCMounts.PIG_ALCHE_B]      = PCMounts.PIG_ALCHE,
	[PCMounts.OSTRICH_BARD_B]   = PCMounts.OSTRICH_BARD,
	[PCMounts.OSTRICH_DANCER_B] = PCMounts.OSTRICH_DANCER,

	-------------------------------
	-- Baby Extended 2nd Classes --
	-------------------------------
	[PCMounts.BIKE_REBELLION_B] = PCMounts.BIKE_REBELLION,
	[PCMounts.FROG_KAGEROU_B]   = PCMounts.FROG_KAGEROU,
	[PCMounts.FROG_OBORO_B]     = PCMounts.FROG_OBORO,
	[PCMounts.PORING_STAR_B]    = PCMounts.PORING_STAR,
	[PCMounts.FROG_LINKER_B]    = PCMounts.FROG_LINKER,

	----------------------
	-- Baby 3rd Classes --
	----------------------
	[PCMounts.LION_RUNE_KNIGHT_B]  = PCMounts.LION_RUNE_KNIGHT,
	[PCMounts.FOX_WARLOCK_B]       = PCMounts.FOX_WARLOCK,
	[PCMounts.OSTRICH_RANGER_B]    = PCMounts.OSTRICH_RANGER,
	[PCMounts.SHEEP_BISHOP_B]      = PCMounts.SHEEP_BISHOP,
	[PCMounts.PIG_MECHANIC_B]      = PCMounts.PIG_MECHANIC,
	[PCMounts.HYENA_G_CROSS_B]     = PCMounts.HYENA_G_CROSS,

	[PCMounts.LION_ROYAL_GUARD_B]  = PCMounts.LION_ROYAL_GUARD,
	[PCMounts.FOX_SORCERER_B]      = PCMounts.FOX_SORCERER,
	[PCMounts.OSTRICH_MINSTREL_B]  = PCMounts.OSTRICH_MINSTREL,
	[PCMounts.OSTRICH_WANDERER_B]  = PCMounts.OSTRICH_WANDERER,
	[PCMounts.SHEEP_SURA_B]        = PCMounts.SHEEP_SURA,
	[PCMounts.PIG_GENETIC_B]       = PCMounts.PIG_GENETIC,
	[PCMounts.HYENA_S_CHASER_B]    = PCMounts.HYENA_S_CHASER,

	-------------------------------
	-- Baby Extended 3rd Classes --
	-------------------------------
	[PCMounts.HAETAE_STAR_EMPEROR_B] = PCMounts.HAETAE_STAR_EMPEROR,
	[PCMounts.HAETAE_SOUL_REAPER_B]  = PCMounts.HAETAE_SOUL_REAPER,

	------------------------
	-- Baby Doram Classes --
	------------------------
	[PCMounts.SUMM_MOUNT_B]        = PCMounts.SUMM_MOUNT,
}
