Enable Druid classes (2026): the English skill and job files it can copy for you.

These five files are from ROenglishRE, the English translation project by zackdreaver, continued by
llchrisll (https://github.com/llchrisll/ROenglishRE), release of 2026-10-07 (commit f7d270ec), as its
Tools/ClientGenerator.bat writes them for a 2025-07-16 client (Renewal, client date 2025-06-18). Each
file keeps its own header; they are llchrisll's work, not part of this patch.

Added to them, for the Druid line (Druid, Karnos, Alitea and the babies):
  skillid.lub        AT_PLUME_PIERCER, AT_NATURE_RAGE and 44 newer kRO skill ids
  skillinfolist.lub  Plume Piercer and Nature Rage
  skilldescript.lub  Plume Piercer and Nature Rage; Pinion Shot's level 3 reads 7800% (kRO 2026-10-07)
  skilltreeview.lub  the Druid, Karnos and Alitea trees and their tabs (Druid / 2nd / 3rd)
  pcjobname.lub      Druid, Karnos, Alitea, Baby Druid, Baby Karnos
Costs and numbers are kRO 2026-10-07's. Rebuilt with tools/druid_re/ro_druid_merge.py (LGN_WARP).

The patch copies them under data\luafiles514\lua files\ of the folder you choose, and first keeps any
copy already there in EnableDruidClasses_backup\ beside that data folder. The client reads loose files
over the GRF only when it is patched with "Read data folder first".
