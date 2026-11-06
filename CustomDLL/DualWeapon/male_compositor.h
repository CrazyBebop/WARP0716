/* Male-only extension. Female reference/contacts are deliberately independent. */
#include "male_profile.h"
#include "male_axe_profile.h"

static int male_name(u32 resource,const char *stem,int sprite)
{
	const u8 *name;
	u32 i=0;
	if(!resource) return 0;
	name=(const u8 *)(resource+0x14);
	while(stem[i] && i<220) { if(name[i]!=(u8)stem[i]) return 0; i++; }
	if(stem[i] || name[i++]!='.') return 0;
	if(sprite) return name[i]=='s' && name[i+1]=='p' && name[i+2]=='r' && !name[i+3];
	return name[i]=='a' && name[i+1]=='c' && name[i+2]=='t' && !name[i+3];
}
static int male_weapon_family(u32 resource,int shadow)
{
	static const u8 assassin[]="sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\\xbe\xee\xbc\xbc\xbd\xc5\\\xbe\xee\xbc\xbc\xbd\xc5_\xb3\xb2_";
	static const u8 cross[]="sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\shadow_cross\\shadow_cross_\xb3\xb2_";
	const u8 *prefix=shadow?cross:assassin,*name;
	u32 i;
	if(!resource) return 0;
	name=(const u8 *)(resource+0x14);
	for(i=0;prefix[i];i++) if(name[i]!=prefix[i]) return 0;
	return 1;
}
static int male_view(u32 view)
{
	int i;
	for(i=0;i<DWM_VIEW_COUNT;i++) if(view==DWM_VIEWS[i]) return i;
	if(view>=58 && view<=61) return DWM_VIEW_COUNT+(int)view-58;
	return -1;
}
static int male_fingerprint(Layer *l,Image *im,const DWMFingerprint *f)
{
	return l && im && l->kind==0 && l->x==f->x && l->y==f->y &&
		l->index==f->index && l->mirror==f->mirror && l->sx==1 && l->sy==1 &&
		l->angle==0 && im->width==f->width && im->height==f->height && !im->columns && !im->rows;
}
static int male_native(Prepared *out,Packet *stock,Layer *base,u32 spr,u32 act,int action,int frame)
{
	Layer *l=layer_at(act,action,frame);
	Image *im=image_at(spr,l);
	float sw,sh,sx,sy,ox,oy,w,h;
	u32 frames;
	int i;
	out->visible=0;
	if(!l || !base || !stock->image) return 0;
	frames=rd(rd(act,0x110),action*12);
	if(rd(frames+frame*68,0x24)-(u32)l!=36) return 0;
	if(l->index==-1) return 1;
	if(!im || im->columns || im->rows || !positive(l->sx,16) || !positive(l->sy,16) ||
		!positive(base->sx,16) || !positive(base->sy,16) ||
		stock->image->columns<0 || stock->image->rows<0 ||
		stock->image->columns>16 || stock->image->rows>16) return 0;
	sw=(float)(stock->image->width*(stock->image->columns+1));
	sh=(float)(stock->image->height*(stock->image->rows+1));
	sx=absolute(stock->right-stock->left-1)/(sw*base->sx);
	sy=absolute(stock->bottom-stock->top-1)/(sh*base->sy);
	if(!positive(sx,64) || !positive(sy,64)) return 0;
	ox=stock->left-(base->x+(base->mirror?sw:0))*sx*base->sx;
	oy=stock->top-base->y*sy*base->sy;
	w=(float)im->width; h=(float)im->height;
	for(i=0;i<12;i++) ((u32 *)&out->packet)[i]=((u32 *)stock)[i];
	out->packet.left=ox+(l->x+(l->mirror?w:0))*sx*l->sx;
	out->packet.right=ox+(l->x+(l->mirror?0:w))*sx*l->sx+1;
	out->packet.top=oy+l->y*sy*l->sy;
	out->packet.bottom=oy+(l->y+h)*sy*l->sy+1;
	out->packet.angle=stock->angle-base->angle+l->angle;
	out->packet.image=im; out->palette=(void *)(spr+0x110); out->visible=1;
	return 1;
}
static int male_prepare(Prepared *out,Packet *stock,Layer *base,u32 spr,u32 act,
	const DWMPose *pose,const DWMFingerprint *guide,Layer *body,Image *bodyImage,
	const DWMContact *contact,int phase,int role)
{
	Layer *l;
	Image *im;
	float sw,sh,sx,sy,ox,oy,left,right,top,bottom,cx,cy,tx,ty,w,h,extra,angle,wx,wy;
	u32 frameBase,end;
	int i;
	out->visible=0; out->order=role;
	if(!pose->visible) {
		if(pose->mode!=2) return 1;
		l=layer_at(act,pose->sa,pose->sf);
		return l && l->index==-1;
	}
	l=layer_at(act,pose->sa,pose->sf); im=image_at(spr,l);
	if(!l || !im || !base || !stock->image || l->kind || l->index!=pose->index ||
		l->x!=pose->x || l->y!=pose->y || l->mirror!=pose->sourceMirror ||
		l->sx!=1 || l->sy!=1 || l->angle!=pose->sourceAngle || im->columns || im->rows ||
		im->width!=pose->width || im->height!=pose->height ||
		!positive(base->sx,16) || !positive(base->sy,16) ||
		stock->image->columns<0 || stock->image->rows<0 ||
		stock->image->columns>16 || stock->image->rows>16) return 0;
	frameBase=rd(rd(act,0x110),pose->sa*12);
	end=rd(frameBase+pose->sf*68,0x24);
	if(end-(u32)l!=36) return 0;
	sw=(float)(stock->image->width*(stock->image->columns+1));
	sh=(float)(stock->image->height*(stock->image->rows+1));
	sx=absolute(stock->right-stock->left-1)/(sw*base->sx);
	sy=absolute(stock->bottom-stock->top-1)/(sh*base->sy);
	if(!positive(sx,64) || !positive(sy,64)) return 0;
	ox=stock->left-(base->x+(base->mirror?sw:0))*sx*base->sx;
	oy=stock->top-base->y*sy*base->sy;
	extra=stock->angle-base->angle; angle=pose->angle+extra;
	if(!phase && pose->mode==0) {
		left=ox+(body->x+(body->mirror?bodyImage->width:0))*sx;
		right=ox+(body->x+(body->mirror?0:bodyImage->width))*sx+1;
		top=oy+body->y*sy; bottom=oy+(body->y+bodyImage->height)*sy+1;
		tx=(contact->bx/bodyImage->width-0.5f)*(right-left)+contact->dx*sx;
		ty=(contact->by/bodyImage->height-0.5f)*(bottom-top)+contact->dy*sy;
		wx=contact->wx; wy=contact->wy;
	} else {
		left=ox+(guide->x+(guide->mirror?guide->width:0))*sx;
		right=ox+(guide->x+(guide->mirror?0:guide->width))*sx+1;
		top=oy+guide->y*sy; bottom=oy+(guide->y+guide->height)*sy+1;
		tx=(pose->gx/guide->width-0.5f)*(right-left);
		ty=(pose->gy/guide->height-0.5f)*(bottom-top);
		wx=pose->wx; wy=pose->wy;
	}
	if(!rotate_extra(&tx,&ty,extra)) return 0;
	cx=(left+right)*0.5f+tx; cy=(top+bottom)*0.5f+ty;
	tx=(wx-im->width*0.5f)*(pose->mirror?-sx:sx);
	ty=(wy-im->height*0.5f)*sy;
	if(!rotate_extra(&tx,&ty,angle)) return 0;
	cx-=tx; cy-=ty; w=im->width*sx; h=im->height*sy;
	if(!positive(w,32768) || !positive(h,32768)) return 0;
	for(i=0;i<12;i++) ((u32 *)&out->packet)[i]=((u32 *)stock)[i];
	out->packet.left=cx+(pose->mirror?w:-w)*0.5f;
	out->packet.right=cx+(pose->mirror?-w:w)*0.5f;
	out->packet.top=cy-h*0.5f; out->packet.bottom=cy+h*0.5f;
	out->packet.angle=angle; out->packet.image=im;
	out->palette=(void *)(spr+0x110); out->visible=1;
	return 1;
}
static int compose_male(void *actor,Packet *packet,void *palette,u32 a3,float a4,float a5,
	u32 a6,u32 *ctx,Draw draw,Row *row,int offOnly)
{
	u32 ap=(u32)actor,sv,se,av,ae,bodyAct,bodySpr,views,sourceSpr[2],sourceAct[2],stockSpr;
	int bi=-1,i,phase=-1,d=0,f,action,vi[2],role[2],channel;
	Layer *body,*base,*trail;
	Image *bodyImage,*stockImage,*trailImage;
	Prepared hands[2];
	const DWMFingerprint *bodyCell,*guide;
	if(row->offType!=1 && row->offType!=2 && row->offType!=6) return 0;
	if(!offOnly && row->mainType!=1 && row->mainType!=2 && row->mainType!=6) return 0;
	action=rd(ap,ctx[5]); f=rd(ap,ctx[6]);
	if(action>=32 && action<40 && f>=0 && f<6) { phase=0; d=action-32; }
	else if(!offOnly && action>=88 && action<96 && f>=0 && f<8) { phase=1; d=action-88; }
	else if(!offOnly) return 0;
	sv=rd(ap,0x4ac); se=rd(ap,0x4b0); av=rd(ap,0x4b8); ae=rd(ap,0x4bc);
	if(!sv || se<sv || se-sv<28 || se-sv>128 || !av || ae<av || ae-av<4 || ae-av>64) return 0;
	bodyAct=rd(av,0); bodySpr=rd(sv,0);
	for(i=0;i<5;i++) if(male_name(bodyAct,DWM_BODY_NAMES[i],0) && male_name(bodySpr,DWM_BODY_NAMES[i],1)) { bi=i; break; }
	if(bi<0 || !male_weapon_family(row->offAct,bi==4) || !male_weapon_family(row->offSpr,bi==4) ||
		(!offOnly && (!male_weapon_family(row->mainAct,bi==4) || !male_weapon_family(row->mainSpr,bi==4)))) return 0;
	views=ctx[18]?ctx[18]+((ap>>4)&255)*8:0;
	if(!views) return 0;
	vi[0]=male_view(rd(views,0)); vi[1]=male_view(rd(views,4));
	if(vi[1]<0 || (!offOnly && vi[0]<0)) return 0;
	base=layer_at(row->stockAct,action,f); stockSpr=rd(sv,20); stockImage=image_at(stockSpr,base);
	trail=layer_at(row->stockTrailAct,action,f); trailImage=image_at(rd(sv,24),trail);
	channel=stockImage && stockImage==packet->image && palette==(void *)(stockSpr+0x110)?5:0;
	if(trailImage && trailImage==packet->image && palette==(void *)(rd(sv,24)+0x110)) {
		if(channel) return 0;
		channel=6;
	}
	if(!channel) return 0;
	if(phase<0) {
		/* Other off-only actions use the original native ACT frame. No held
		 * contact or dual attack timeline is imposed on walking/sitting/solo. */
		if(!male_native(&hands[0],packet,channel==5?base:trail,
			channel==5?row->offSpr:row->offTrailSpr,channel==5?row->offAct:row->offTrailAct,action,f)) return 0;
		if(hands[0].visible) draw(actor,&hands[0].packet,hands[0].palette,a3,a4,a5,a6);
		return 1;
	}
	body=layer_at(bodyAct,action,f); bodyImage=image_at(bodySpr,body);
	bodyCell=&DWM_BODIES[bi][phase][d][f]; guide=&DWM_GUIDES[phase][d][f];
	if(!male_fingerprint(body,bodyImage,bodyCell)) return 0;
	/* Channel6 is the native slash-effect artwork. Leave its original packet
	 * untouched; only the owned channel5 combined weapon bitmap is replaced. */
	if(channel!=5) return 0;
	sourceSpr[0]=row->mainSpr; sourceAct[0]=row->mainAct;
	sourceSpr[1]=row->offSpr; sourceAct[1]=row->offAct;
	/* In the unmirrored male front/rear art, the short-blade trajectory
	 * belongs to the right arm. Native body mirroring exchanges the roles. */
	role[0]=1-body->mirror; role[1]=body->mirror;
	for(i=offOnly?1:0;i<2;i++) {
		if(!male_prepare(&hands[i],packet,base,sourceSpr[i],sourceAct[i],
			vi[i]<DWM_VIEW_COUNT?&DWM_POSES[vi[i]][phase][d][f][role[i]]:
				&DWMA_POSES[vi[i]-DWM_VIEW_COUNT][phase][d][f][role[i]],guide,body,bodyImage,
			phase?0:(vi[i]<DWM_VIEW_COUNT?&DWM_CONTACTS[bi][vi[i]][d][f][role[i]]:
				&DWMA_CONTACTS[bi][vi[i]-DWM_VIEW_COUNT][d][f][role[i]]),phase,role[i])) return 0;
	}
	for(i=0;i<2;i++) {
		int logical=role[0]==i?0:1;
		if(offOnly && logical==0) continue;
		if(hands[logical].visible) draw(actor,&hands[logical].packet,hands[logical].palette,a3,a4,a5,a6);
	}
	return 1;
}
