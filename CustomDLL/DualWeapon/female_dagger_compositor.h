/* Missing female daggers use measured source fingerprints and native guides.
 * male_prepare is the shared pixel-to-packet math; no male coordinates enter
 * this path. The established seventeen female views remain unchanged. */
#include "female_dagger_profile.h"
static int female_dagger_name(u32 spr,u32 act,u32 view)
{
	static const char *const names[3]={
		"sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\\xbe\xee\xbc\xbc\xbd\xc5\\\xbe\xee\xbc\xbc\xbd\xc5_\xbf\xa9_1207",
		"sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\\xbe\xee\xbc\xbc\xbd\xc5\\\xbe\xee\xbc\xbc\xbd\xc5_\xbf\xa9_1216",
		"sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\\xbe\xee\xbc\xbc\xbd\xc5\\\xbe\xee\xbc\xbc\xbd\xc5_\xbf\xa9_1219"
	};
	return view>=31 && view<=33 && male_name(act,names[view-31],0) && male_name(spr,names[view-31],1);
}
static int female_dagger_prepare(Prepared *out,Packet *stock,Layer *base,u32 spr,u32 act,
	u32 view,Layer *body,Image *bodyImage,const DWNativeBasis *basis,int phase,int dir,int frame,int hand)
{
	if(!female_dagger_name(spr,act,view)) return 0;
	if(!male_prepare(out,stock,base,spr,act,&DWF_POSES[view-31][phase][dir][frame][hand],
		&DWF_GUIDES[phase][dir][frame],body,bodyImage,
		phase?0:&DWF_CONTACTS[view-31][dir][frame][hand],phase,hand)) return 0;
	out->order=basis->hands[hand].order;
	return 1;
}
