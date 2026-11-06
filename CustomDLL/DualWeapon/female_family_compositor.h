/* Per-body female profiles. The accepted Cross path remains in compositor.c. */
#include "female_family_profile.h"
static int female_body(u32 act,u32 spr)
{
	int i;
	for(i=0;i<5;i++) if(male_name(act,DWFF_NAMES[i],0) && male_name(spr,DWFF_NAMES[i],1)) return i;
	return -1;
}
static int female_family_prepare(Prepared *out,Packet *stock,Layer *base,u32 spr,u32 act,
	u32 view,int bi,Layer *body,Image *bodyImage,const DWNativeBasis *basis,int phase,int dir,int frame,int hand)
{
	int vi;
	u32 key=(bi==4 && view==2)?10002:view;
	for(vi=0;vi<DWFF_COUNT;vi++) if(DWFF_KEYS[vi]==key) break;
	if(vi==DWFF_COUNT || bi<0 || bi>=5) return 0;
	if(!male_prepare(out,stock,base,spr,act,&DWFF_POSES[vi][phase][dir][frame][hand],
		&DWF_GUIDES[phase][dir][frame],body,bodyImage,
		phase?0:&DWFF_CONTACTS[bi][vi][dir][frame][hand],phase,hand)) return 0;
	out->order=basis->hands[hand].order;
	return 1;
}
