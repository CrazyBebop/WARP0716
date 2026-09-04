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
*   Last Modified : 2022-08-23                                             *
*                                                                          *
****************************************************************************
]]--

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`··´¯)
( \                                                  / )
 ( ) Default set of prefixes used for palette files ( )
  (/                                                \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´)

]]--

PCPals =
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

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCIds.HYPER_NOVICE] = "HYPER_NOVICE",
	[PCIds.REBELLION]    = "¸®º§¸®¿Â",
	[PCIds.KAGEROU]      = "KAGEROU",
	[PCIds.OBORO]        = "OBORO",

	-----------------
	-- 3rd Classes --
	-----------------
	[PCIds.RUNE_KNIGHT]    = "·é³ªÀÌÆ®",
	[PCIds.RUNE_MOUNT]     = "·éµå·¡°ï",
	[PCIds.WARLOCK]        = "¿ö·Ï",
	[PCIds.RANGER]         = "·¹ÀÎÀú",
	[PCIds.RANGER_MOUNT]   = "¿ïÇÁ·¹ÀÎÀú",
	[PCIds.ARCHBISHOP]     = "¾ÆÅ©ºñ¼ó",
	[PCIds.MECHANIC]       = "¹ÌÄÉ´Ð",
	[PCIds.MADOGEAR]       = "¹ÌÄÉ´Ð_¸¶µµ±â¾î",
	[PCIds.GUILLOTINE_X]   = "±æ·ÎÆ¾Å©·Î½º",

	[PCIds.ROYAL_GUARD]    = "·Î¾â°¡µå",
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

	-----------------------
	-- Doram 1st Classes --
	-----------------------
	[PCIds.SUMMONER]   = "¹¦Á·",

	-----------------------
	-- Doram 2nd Classes --
	-----------------------
	[PCIds.SPIRIT_HANDLER]   = "SPIRIT_HANDLER",

	--[[
	 __  __   ___   _   _  _  _  _____     ___  ___   ___
	|  \/  | / _ \ | | | || \| ||_   _|   |_ _||   \ / __|
	| |\/| || (_) || |_| || .  |  | |      | | | |) |\__ \
	|_|  |_| \___/  \___/ |_|\_|  |_|     |___||___/ |___/

	]]--

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCMounts.BIKE_GUNNER]      = "°Ç³Ê",
	[PCMounts.FROG_NINJA]       = "´ÑÀÚ",

	-----------------
	-- 2nd Classes --
	-----------------
	[PCMounts.LION_CRUSADER]    = "Å©·ç",
	[PCMounts.SHEEP_MONK]       = "¸ùÅ©",
	[PCMounts.FOX_SAGE]         = "¼¼ÀÌÁö",
	[PCMounts.HYENA_ROGUE]      = "·Î±×",
	[PCMounts.PIG_ALCHE]        = "¿¬±Ý¼ú»ç",
	[PCMounts.OSTRICH_BARD]     = "¹Ùµå",
	[PCMounts.OSTRICH_DANCER]   = "´í¼­",

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCMounts.SHEEP_HI_PRIEST]  = "ÇÏÀÌÇÁ¸®½ºÆ®",
	[PCMounts.FOX_HI_WIZ]       = "ÇÏÀÌÀ§Àúµå",
	[PCMounts.PIG_WHITESMITH]   = "È­ÀÌÆ®½º¹Ì½º",
	[PCMounts.OSTRICH_SNIPER]   = "½º³ªÀÌÆÛ",
	[PCMounts.HYENA_SIN_X]      = "¾î¼¼½ÅÅ©·Î½º",

	[PCMounts.LION_PALADIN]     = "ÆÈ¶óµò",
	[PCMounts.SHEEP_CHAMP]      = "Ã¨ÇÇ¿Â",
	[PCMounts.FOX_PROF]         = "ÇÁ·ÎÆä¼­",
	[PCMounts.HYENA_STALKER]    = "½ºÅäÄ¿",
	[PCMounts.PIG_CREATOR]      = "Å©¸®¿¡ÀÌÅÍ",
	[PCMounts.OSTRICH_CLOWN]    = "Å©¶ó¿î",
	[PCMounts.OSTRICH_GYPSY]    = "Áý½Ã",

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCMounts.PORING_H_NOVICE]  = "HYPER_NOVICE_RIDING",
	[PCMounts.PORING_STAR]      = "±Ç¼º",

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
	[PCMounts.SUMM_MOUNT] = "°í¾çÀÌÄ«Æ®",

	-----------------------
	-- Doram 2nd Classes --
	-----------------------
	[PCMounts.SP_HANDLER_MOUNT] = "SPIRIT_HANDLER_RIDING",
}

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸·´¯)
( \                                   / )
 ( ) Prefix overrides for Langtype 0 ( )
  (/                                 \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·)

]]--

PCPals.LT_0 =
{
	--[[
	    _   ___   ___     ___  ___   ___
	 _ | | / _ \ | _ )   |_ _||   \ / __|
	| || || (_) || _ \    | | | |) |\__ \
	 \__/  \___/ |___/   |___||___/ |___/

	]]--

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCIds.GUNSLINGER]   = "°Ç³Ê",
	[PCIds.NINJA]        = "´ÑÀÚ",

	-----------------
	-- 2nd Classes --
	-----------------
	[PCIds.CRUSADER]    = "Å©·ç",
	[PCIds.CRUS_MOUNT]  = "ÆäÄÚÆäÄÚ_Å©·ç",
	[PCIds.MONK]        = "¸ùÅ©",
	[PCIds.SAGE]        = "¼¼ÀÌÁö",
	[PCIds.ROGUE]       = "·Î±×",
	[PCIds.ALCHEMIST]   = "¿¬±Ý¼ú»ç",
	[PCIds.BARD]        = "¹Ùµå",
	[PCIds.DANCER]      = "´í¼­",

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCIds.LORD_KNIGHT] = "·Îµå³ªÀÌÆ®",
	[PCIds.LORD_MOUNT]  = "ÆäÄÚ·Î³ª",
	[PCIds.HIGH_PRIEST] = "ÇÏÀÌÇÁ¸®½ºÆ®",
	[PCIds.HIGH_WIZARD] = "ÇÏÀÌÀ§Àúµå",
	[PCIds.WHITESMITH]  = "È­ÀÌÆ®½º¹Ì½º",
	[PCIds.SNIPER]      = "½º³ªÀÌÆÛ",
	[PCIds.ASSASSIN_X]  = "¾î½Ø½ÅÅ©·Î½º",

	[PCIds.PALADIN]     = "ÆÈ¶óµò",
	[PCIds.PAL_MOUNT]   = "ÆäÄÚÆÈ¶ó", --Peco mount for Paladin
	[PCIds.CHAMPION]    = "Ã¨ÇÇ¿Â",
	[PCIds.PROFESSOR]   = "ÇÁ·ÎÆä¼­",
	[PCIds.STALKER]     = "½ºÅäÄ¿",
	[PCIds.CREATOR]     = "Å©¸®¿¡ÀÌÅÍ",
	[PCIds.CLOWN]       = "Å©¶ó¿î",
	[PCIds.GYPSY]       = "Áý½Ã",

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCIds.STAR_GLAD]    = "±Ç¼º",
	[PCIds.SOUL_LINKER]  = "¼Ò¿ï¸µÄ¿",
}

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯)
( \                                                      / )
 ( ) Inheritance table for mapping ids with same prefix ( )
  (/                                                    \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.)

]]--

PCPalInheritTbl =
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
	[PCIds.GUNSLINGER]   = PCIds.NOVICE,
	[PCIds.NINJA]        = PCIds.NOVICE,

	-------------------------------
	-- Baby Extended 1st Classes --
	-------------------------------
	[PCIds.SUPERNOVICE_B]  = PCIds.SUPERNOVICE,
	[PCIds.SUPERNOVICE2_B] = PCIds.SUPERNOVICE,
	[PCIds.GUNSLINGER_B]   = PCIds.GUNSLINGER,
	[PCIds.NINJA_B]        = PCIds.NINJA,
	[PCIds.TAEKWON_B]      = PCIds.TAEKWON,

	-----------------
	-- 2nd Classes --
	-----------------
	[PCIds.CRUSADER]   = PCIds.KNIGHT,
	[PCIds.CRUS_MOUNT] = PCIds.KNIGHT_MOUNT,
	[PCIds.MONK]       = PCIds.PRIEST,
	[PCIds.SAGE]       = PCIds.WIZARD,
	[PCIds.ROGUE]      = PCIds.ASSASSIN,
	[PCIds.ALCHEMIST]  = PCIds.BLACKSMITH,
	[PCIds.BARD]       = PCIds.HUNTER,
	[PCIds.DANCER]     = PCIds.HUNTER,

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

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCIds.LORD_KNIGHT] = PCIds.KNIGHT,
	[PCIds.LORD_MOUNT]  = PCIds.KNIGHT_MOUNT,
	[PCIds.HIGH_PRIEST] = PCIds.PRIEST,
	[PCIds.HIGH_WIZARD] = PCIds.WIZARD,
	[PCIds.WHITESMITH]  = PCIds.BLACKSMITH,
	[PCIds.SNIPER]      = PCIds.HUNTER,
	[PCIds.ASSASSIN_X]  = PCIds.ASSASSIN,

	[PCIds.PALADIN]     = PCIds.KNIGHT,
	[PCIds.PAL_MOUNT]   = PCIds.KNIGHT_MOUNT,
	[PCIds.CHAMPION]    = PCIds.PRIEST,
	[PCIds.PROFESSOR]   = PCIds.WIZARD,
	[PCIds.STALKER]     = PCIds.KNIGHT,
	[PCIds.CREATOR]     = PCIds.BLACKSMITH,
	[PCIds.CLOWN]       = PCIds.HUNTER,
	[PCIds.GYPSY]       = PCIds.HUNTER,

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCIds.STAR_GLAD]    = PCIds.TAEKWON,
	[PCIds.STAR_GLAD_F]  = PCIds.STAR_GLAD,
	[PCIds.SOUL_LINKER]  = PCIds.TAEKWON,

	-------------------------------
	-- Baby Extended 2nd Classes --
	-------------------------------
	[PCIds.REBELLION_B]    = PCIds.REBELLION,
	[PCIds.KAGEROU_B]      = PCIds.KAGEROU,
	[PCIds.OBORO_B]        = PCIds.OBORO,
	[PCIds.STAR_GLAD_B]    = PCIds.STAR_GLAD,
	[PCIds.STAR_GLAD_F_B]  = PCIds.STAR_GLAD,
	[PCIds.SOUL_LINKER_B]  = PCIds.SOUL_LINKER,

	-----------------
	-- 3rd Classes --
	-----------------
	[PCIds.RUNE_MOUNT2]    = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT3]    = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT4]    = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT5]    = PCIds.RUNE_MOUNT,

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
	[PCIds.RUNE_MOUNT2_H]   = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT3_H]   = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT4_H]   = PCIds.RUNE_MOUNT,
	[PCIds.RUNE_MOUNT5_H]   = PCIds.RUNE_MOUNT,
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

	--------------------------
	-- Extended 3rd Classes --
	--------------------------
	[PCIds.STAR_EMPEROR_F] = PCIds.STAR_EMPEROR,

	-------------------------------
	-- Baby Extended 3rd Classes --
	-------------------------------
	[PCIds.STAR_EMPEROR_B]   = PCIds.STAR_EMPEROR,
	[PCIds.STAR_EMPEROR_F_B] = PCIds.STAR_EMPEROR,
	[PCIds.SOUL_REAPER_B]    = PCIds.SOUL_REAPER,

	--------------
	-- Costumes --
	--------------
	[PCIds.SANTA]        = PCIds.PRIEST,
	[PCIds.SUMMER]       = PCIds.PRIEST,
	[PCIds.HANBOK]       = PCIds.PRIEST,
	[PCIds.OKTOBERFEST]  = PCIds.PRIEST,
	[PCIds.SUMMER2]      = PCIds.PRIEST,

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

	-----------------
	-- 1st Classes --
	-----------------
	[PCMounts.PORING_NOVICE]    = PCIds.NOVICE,
	[PCMounts.PECO_SWORD]       = PCIds.SWORDMAN,
	[PCMounts.FOX_MAGICIAN]     = PCIds.MAGICIAN,
	[PCMounts.OSTRICH_ARCHER]   = PCIds.ARCHER,
	[PCMounts.SHEEP_ACO]        = PCIds.ACOLYTE,
	[PCMounts.PIG_MERCHANT]     = PCIds.MERCHANT,
	[PCMounts.HYENA_THIEF]      = PCIds.THIEF,

	----------------------
	-- Baby 1st Classes --
	----------------------
	[PCMounts.PORING_NOVICE_B]  = PCIds.NOVICE,
	[PCMounts.PECO_SWORD_B]     = PCIds.SWORDMAN,
	[PCMounts.FOX_MAGICIAN_B]   = PCIds.MAGICIAN,
	[PCMounts.OSTRICH_ARCHER_B] = PCIds.ARCHER,
	[PCMounts.SHEEP_ACO_B]      = PCIds.ACOLYTE,
	[PCMounts.PIG_MERCHANT_B]   = PCIds.MERCHANT,
	[PCMounts.HYENA_THIEF_B]    = PCIds.THIEF,

	------------------------------
	-- Transcendent 1st Classes --
	------------------------------
	[PCMounts.PORING_NOVICE_H]  = PCIds.NOVICE,
	[PCMounts.PECO_SWORD_H]     = PCIds.SWORDMAN,
	[PCMounts.FOX_MAGICIAN_H]   = PCIds.MAGICIAN,
	[PCMounts.OSTRICH_ARCHER_H] = PCIds.ARCHER,
	[PCMounts.SHEEP_ACO_H]      = PCIds.ACOLYTE,
	[PCMounts.PIG_MERCHANT_H]   = PCIds.MERCHANT,
	[PCMounts.HYENA_THIEF_H]    = PCIds.THIEF,

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCMounts.PORING_S_NOVICE]  = PCIds.SUPERNOVICE,
	[PCMounts.PORING_S_NOVICE2] = PCIds.SUPERNOVICE,
	[PCMounts.PORING_TAEKWON]   = PCIds.TAEKWON,

	-------------------------------
	-- Baby Extended 1st Classes --
	-------------------------------
	[PCMounts.PORING_S_NOVICE_B]  = PCIds.SUPERNOVICE,
	[PCMounts.PORING_S_NOVICE2_B] = PCIds.SUPERNOVICE,
	[PCMounts.BIKE_GUNNER_B]      = PCMounts.BIKE_GUNNER,
	[PCMounts.FROG_NINJA_B]       = PCMounts.FROG_NINJA,
	[PCMounts.PORING_TAEKWON_B]   = PCIds.TAEKWON,

	-----------------
	-- 2nd Classes --
	-----------------
	[PCMounts.LION_KNIGHT]      = PCIds.KNIGHT,
	[PCMounts.SHEEP_PRIEST]     = PCIds.PRIEST,
	[PCMounts.FOX_WIZARD]       = PCIds.WIZARD,
	[PCMounts.PIG_BLACKSMITH]   = PCIds.BLACKSMITH,
	[PCMounts.OSTRICH_HUNTER]   = PCIds.HUNTER,
	[PCMounts.HYENA_ASSASSIN]   = PCIds.ASSASSIN,

	----------------------
	-- Baby 2nd Classes --
	----------------------
	[PCMounts.LION_KNIGHT_B]    = PCIds.KNIGHT,
	[PCMounts.SHEEP_PRIEST_B]   = PCIds.PRIEST,
	[PCMounts.FOX_WIZARD_B]     = PCIds.WIZARD,
	[PCMounts.PIG_BLACKSMITH_B] = PCIds.BLACKSMITH,
	[PCMounts.OSTRICH_HUNTER_B] = PCIds.HUNTER,
	[PCMounts.HYENA_ASSASSIN_B] = PCIds.ASSASSIN,

	[PCMounts.LION_CRUSADER_B]  = PCMounts.LION_CRUSADER,
	[PCMounts.SHEEP_MONK_B]     = PCMounts.SHEEP_MONK,
	[PCMounts.FOX_SAGE_B]       = PCMounts.FOX_SAGE,
	[PCMounts.HYENA_ROGUE_B]    = PCMounts.HYENA_ROGUE,
	[PCMounts.PIG_ALCHE_B]      = PCMounts.PIG_ALCHE,
	[PCMounts.OSTRICH_BARD_B]   = PCMounts.OSTRICH_BARD,
	[PCMounts.OSTRICH_DANCER_B] = PCMounts.OSTRICH_DANCER,

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCMounts.LION_LORD_KNIGHT] = PCIds.KNIGHT,

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCMounts.BIKE_REBELLION]   = PCIds.REBELLION,
	[PCMounts.FROG_KAGEROU]     = PCIds.KAGEROU,
	[PCMounts.FROG_OBORO]       = PCIds.OBORO,
	[PCMounts.FROG_LINKER]      = PCIds.TAEKWON,

	-------------------------------
	-- Baby Extended 2nd Classes --
	-------------------------------
	[PCMounts.BIKE_REBELLION_B] = PCIds.REBELLION,
	[PCMounts.FROG_KAGEROU_B]   = PCIds.KAGEROU,
	[PCMounts.FROG_OBORO_B]     = PCIds.OBORO,
	[PCMounts.PORING_STAR_B]    = PCMounts.PORING_STAR,
	[PCMounts.FROG_LINKER_B]    = PCIds.TAEKWON,

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
	[PCMounts.SUMM_MOUNT_B] = PCMounts.SUMM_MOUNT,
}

--[[

(¯`·¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·´¯)
( \                                        / )
 ( ) Inheritance overrides for Langtype 0 ( )
  (/                                      \)
   (.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸¸.·)

]]--

PCPalInheritTbl.LT_0 =
{
	--[[
	    _   ___   ___     ___  ___   ___
	 _ | | / _ \ | _ )   |_ _||   \ / __|
	| || || (_) || _ \    | | | |) |\__ \
	 \__/  \___/ |___/   |___||___/ |___/

	]]--

	--------------------------
	-- Extended 1st Classes --
	--------------------------
	[PCIds.GUNSLINGER] = -1, --no mapping required since prefix is available
	[PCIds.NINJA]      = -1,

	-----------------
	-- 2nd Classes --
	-----------------
	[PCIds.CRUSADER]   = -1, --no mapping required since prefix is available
	[PCIds.CRUS_MOUNT] = -1,
	[PCIds.MONK]       = -1,
	[PCIds.SAGE]       = -1,
	[PCIds.ROGUE]      = -1,
	[PCIds.ALCHEMIST]  = -1,
	[PCIds.BARD]       = -1,
	[PCIds.DANCER]     = -1,

	------------------------------
	-- Transcendent 2nd Classes --
	------------------------------
	[PCIds.LORD_KNIGHT] = -1, --no mapping required since prefix is available
	[PCIds.LORD_MOUNT]  = -1,
	[PCIds.HIGH_PRIEST] = -1,
	[PCIds.HIGH_WIZARD] = -1,
	[PCIds.WHITESMITH]  = -1,
	[PCIds.SNIPER]      = -1,
	[PCIds.ASSASSIN_X]  = -1,

	[PCIds.PALADIN]     = -1,
	[PCIds.PAL_MOUNT]   = -1,
	[PCIds.CHAMPION]    = -1,
	[PCIds.PROFESSOR]   = -1,
	[PCIds.STALKER]     = -1,
	[PCIds.CREATOR]     = -1,
	[PCIds.CLOWN]       = -1,
	[PCIds.GYPSY]       = -1,

	--------------------------
	-- Extended 2nd Classes --
	--------------------------
	[PCIds.STAR_GLAD]    = -1, --no mapping required since prefix is available
	[PCIds.SOUL_LINKER]  = -1,
}

-- Custom job palette paths (use Novice palette)

