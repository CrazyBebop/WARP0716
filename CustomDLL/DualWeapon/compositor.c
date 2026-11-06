/*
 * Original-resource compositor, 2025-07-16 x86 Ragexe.
 * No renderer globals, resource mutation, CRT, texture fabrication or image cache.
 * ABI/layout proof: https://github.com/CrazyBebop/WARP0716/pull/69.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef short s16;
#include "native_basis.h"
#include "grip_profile.h"
#include "held_edge_contacts.h"
typedef struct { int x,y,index,mirror; u32 color; float sx,sy; int angle,kind; } Layer;
typedef struct { u16 width,height; s16 columns,rows; u32 texture,unknown; } Image;
typedef struct { float top,left,bottom,right,z0,z1; u32 color; float angle; u32 tail[3]; Image *image; } Packet;
typedef struct {
	u32 actor;
	u32 mainSpr,mainAct,mainTrailSpr,mainTrailAct;
	u32 offSpr,offAct,offTrailSpr,offTrailAct;
	u32 stockAct,stockTrailAct,pair,mainType,offType,gender;
} Row;
typedef void (__thiscall *Draw)(void *,Packet *,void *,u32,float,float,u32);
typedef int (__stdcall *Core)(void *,Packet *,void *,u32,float,float,u32,u32 *,Draw);
#pragma pack(push,1)
typedef struct { s8 x,y; u8 flags,meta; s16 angle; } Pose;
typedef struct { u16 view; u8 family,gender,phase,direction,key,type; s16 x,y; u8 mirror; s16 angle; u8 selected; } Grip;
#pragma pack(pop)
typedef struct { Packet packet; void *palette; int visible,order; } Prepared;
static u32 rd(u32 p,u32 o) { return *(u32 *)(p+o); }
static float absolute(float x) { return x<0?-x:x; }
static int positive(float x,float limit) { return x>0 && x<=limit; }

/* Native CAct actions: +110/+114, stride 12. Frames stride 68.
 * Native CActFrame layers: +20/+24, stride 36. Never use LayerGet's
 * shared sentinel or ActGetFrame's frame-zero fallback for an invalid index. */
static Layer *layer_at(u32 act,int action,int frame)
{
	u32 b,e,f,lb,le;
	if (!act || action<0 || frame<0) return 0;
	b=rd(act,0x110); e=rd(act,0x114);
	if (!b || e<b || e-b>12*512 || (u32)action>=(e-b)/12) return 0;
	b=rd(b,action*12); e=rd(rd(act,0x110),action*12+4);
	if (!b || e<b || e-b>68*256 || (u32)frame>=(e-b)/68) return 0;
	f=b+frame*68; lb=rd(f,0x20); le=rd(f,0x24);
	if (!lb || le<lb || le-lb<36 || le-lb>36*128) return 0;
	return (Layer *)lb;
}
static Image *image_at(u32 spr,Layer *layer)
{
	u32 b,e;
	Image *im;
	if (!spr || !layer || layer->index<0 || (u32)layer->kind>1) return 0;
	b=rd(spr,0x510+12*layer->kind); e=rd(spr,0x514+12*layer->kind);
	if (!b || e<b || e-b>4*65536 || (u32)layer->index>=(e-b)/4) return 0;
	im=((Image **)b)[layer->index];
	return im && im->width && im->height ? im : 0;
}
static int prepare(Prepared *out,Packet *stock,Layer *base,u32 spr,u32 act,
	int action,int frame,const Pose *pose,const Grip *grip)
{
	Layer *l;
	Image *im;
	float ux,uy,cx,cy,w,h;
	int dx=0,dy=0,mirror=0,angle=0,i,selected=frame;
	out->visible=0; out->order=pose?(pose->meta&1):0;
	if(pose && (pose->meta&8)) return 1;
	if(grip) { selected=grip->selected; dx=grip->x; dy=grip->y; mirror=grip->mirror; angle=grip->angle; }
	l=layer_at(act,action,selected); im=image_at(spr,l);
	/* A visible pose requires a real image at the specified source frame.
	 * Missing artwork stays stock; do not borrow a previous actor/frame. */
	if(!im || !base || !stock->image) return 0;
	ux=absolute(stock->right-stock->left)/(stock->image->width*absolute(base->sx));
	uy=absolute(stock->bottom-stock->top)/(stock->image->height*absolute(base->sy));
	if(!positive(ux,64) || !positive(uy,64)) return 0;
	cx=(stock->left+stock->right)*0.5f; cy=(stock->top+stock->bottom)*0.5f;
	if(pose) {
		dx+=pose->x; dy+=pose->y; mirror^=(pose->flags>>6)&1; angle+=pose->angle;
		if(!(pose->meta&16)) { dx-=base->x; dy-=base->y; }
	} else {
		dx+=l->x-base->x; dy+=l->y-base->y;
		angle+=l->angle-base->angle;
		mirror^=(l->mirror!=0)^(base->mirror!=0);
	}
	cx+=dx*ux; cy+=dy*uy;
	w=im->width*absolute(l->sx)*ux; h=im->height*absolute(l->sy)*uy;
	if(!positive(w,32768) || !positive(h,32768)) return 0;
	for(i=0;i<12;i++) ((u32 *)&out->packet)[i]=((u32 *)stock)[i];
	/* Canonical poses already encode final image mirroring. The embedded
	 * legacy rig used a delta XOR source-layer mirror; applying that rule
	 * again here cancels canonical mirroring in directions 4 through 7.
	 * Native/off-only transfer retains the original screen-axis orientation. */
	if(!pose) mirror^=stock->right<stock->left;
	out->packet.left=cx+(mirror?w:-w)*0.5f;
	out->packet.right=cx+(mirror?-w:w)*0.5f;
	out->packet.top=cy+(stock->bottom<stock->top?h:-h)*0.5f;
	out->packet.bottom=cy+(stock->bottom<stock->top?-h:h)*0.5f;
	out->packet.angle=stock->angle+(pose ? angle+l->angle-base->angle : angle);
	out->packet.image=im;
	out->palette=(void *)(spr+0x110);
	out->visible=1;
	return 1;
}

/* Rotate a screen displacement through the actor's additional draw angle.
 * Range-reduced sine/cosine polynomials avoid a CRT/import dependency. The
 * ordinary actor angle is zero; nonzero rotations use the same R*[x,y]
 * convention verified in native C4A0D0's final vertex construction. */
static int rotate_extra(float *x,float *y,float degrees)
{
	float a,z,s,c,sign=1,px=*x,py=*y;
	if(degrees==0) return 1;
	if(!(degrees>-100000 && degrees<100000)) return 0;
	while(degrees>180) degrees-=360;
	while(degrees<-180) degrees+=360;
	if(degrees>90) { degrees=180-degrees; sign=-1; }
	else if(degrees<-90) { degrees=-180-degrees; sign=-1; }
	a=degrees*0.01745329251994329577f; z=a*a;
	s=a*(1+z*(-0.1666666666666667f+z*(0.008333333333333333f+
		z*(-0.0001984126984126984f+z*(0.000002755731922398589f+
		z*(-0.00000002505210838544172f+z*0.0000000001605904383682161f))))));
	c=sign*(1+z*(-0.5f+z*(0.04166666666666667f+z*(-0.001388888888888889f+
		z*(0.00002480158730158730f+z*(-0.0000002755731922398589f+
		z*0.000000002087675698786810f))))));
	*x=c*px-s*py; *y=s*px+c*py;
	return 1;
}

/* Selected original image identity, separate from the measured contact edge. */
static const DWGripImage *grip_image(u32 view,Layer *layer,Image *image)
{
	u32 i;
	if(!layer || !image || layer->kind!=0) return 0;
	for(i=0;i<sizeof(DW_GRIP_IMAGES)/sizeof(DW_GRIP_IMAGES[0]);i++) {
		const DWGripImage *g=&DW_GRIP_IMAGES[i];
		if(g->view==view && g->index==layer->index &&
			g->width==image->width && g->height==image->height) return g;
	}
	return 0;
}
static int profiled_view(u32 view)
{
	return view==1 || view==2 || view==6 || (view>=31 && view<=47) || (view>=58 && view<=61);
}
static int body_family(u32 act,int sprite)
{
	static const u8 name[]="\x73\x70\x72\x69\x74\x65\x5c\xc0\xce\xb0\xa3\xc1\xb7\x5c\xb8\xf6\xc5\xeb\x5c\xbf\xa9\x5c\xbe\xee\xbd\xd8\xbd\xc5\xc5\xa9\xb7\xce\xbd\xba\x5f\xbf\xa9\x2e\x61\x63\x74";
	const u8 *text=(const u8 *)(act+0x14);
	u32 i;
	if(!act) return 0;
	for(i=0;i<sizeof(name)-4;i++) if(text[i]!=name[i]) return 0;
	if(sprite) return text[i]=='s' && text[i+1]=='p' && text[i+2]=='r' && !text[i+3];
	return text[i]=='a' && text[i+1]=='c' && text[i+2]=='t' && !text[i+3];
}

static const DWHeldContact *held_contact(u32 view,int dir,int frame,int hand)
{
	u32 i;
	if(dir<0 || dir>=8 || frame<0 || frame>=6 || hand<0 || hand>=2) return 0;
	for(i=0;i<17;i++) if(DW_CONTACT_VIEWS[i]==view) return &DW_HELD_CONTACTS[i][dir][frame][hand];
	return 0;
}

/* Both packet producers use the same actor/camera origin. Reconstruct it
 * from the CURRENT stock weapon packet, then project the exact body texel
 * through native +1 endpoints, body mirroring and current actor rotation.
 * Match measured opaque pixel boundaries at the local fist seam. Coordinates
 * name texture edges (no +0.5); preserve the accepted rig blade angle.
 * No body/SPR/ACT mutation, fixed screen-side inference or last-draw state. */
static int prepare_gripped(Prepared *out,Packet *stock,Layer *base,
	u32 spr,u32 act,u32 view,Layer *body,Image *bodyImage,
	const DWNativeBasis *basis,int hand,int dir,int frame)
{
	const DWNativeReferenceHand *r=&basis->hands[hand];
	const DWGripImage *grip;
	const DWHeldContact *contact=held_contact(view,dir,frame,hand);
	Layer *l;
	Image *im;
	float sw,sh,sx,sy,ox,oy,left,right,top,bottom,cx,cy,tx,ty,w,h,angle,extra;
	u32 frames,layerEnd,layerBytes;
	int i,action,mirror;
	out->visible=0; out->order=r->order;
	if(r->hidden) return 1;
	action=(r->sourceAttack?80:32)+dir;
	l=layer_at(act,action,r->sourceFrame); im=image_at(spr,l);
	grip=grip_image(view,l,im);
	if(!grip || !contact || contact->index!=l->index || !stock->image || !base || !body || !bodyImage) return 0;
	if(im->columns || im->rows || bodyImage->columns || bodyImage->rows ||
		stock->image->columns<0 || stock->image->rows<0 ||
		stock->image->columns>16 || stock->image->rows>16 ||
		!positive(base->sx,16) || !positive(base->sy,16) ||
		l->sx!=1 || l->sy!=1 || l->angle || r->sourceLayer) return 0;
	frames=rd(rd(act,0x110),action*12);
	layerEnd=rd(frames+r->sourceFrame*68,0x24); layerBytes=layerEnd-(u32)l;
	if(layerBytes%36) return 0;
	for(i=1;i<(int)(layerBytes/36);i++) if(image_at(spr,l+i)) return 0;
	sw=(float)(stock->image->width*(stock->image->columns+1));
	sh=(float)(stock->image->height*(stock->image->rows+1));
	sx=absolute(stock->right-stock->left-1)/(sw*base->sx);
	sy=absolute(stock->bottom-stock->top-1)/(sh*base->sy);
	if(!positive(sx,64) || !positive(sy,64)) return 0;
	ox=stock->left-(base->x+(base->mirror?sw:0))*sx*base->sx;
	oy=stock->top-base->y*sy*base->sy;
	left=ox+(body->x+(body->mirror?bodyImage->width:0))*sx;
	right=ox+(body->x+(body->mirror?0:bodyImage->width))*sx+1;
	top=oy+body->y*sy; bottom=oy+(body->y+bodyImage->height)*sy+1;
#ifdef DW_MEASURE_CONTACTS
	/* Offline measurement fixture only. Never install this build. */
	tx=((DW_BODY_GRIPS[0][dir][frame].grip[hand][0]+0.5f)/bodyImage->width-0.5f)*(right-left);
	ty=((DW_BODY_GRIPS[0][dir][frame].grip[hand][1]+0.5f)/bodyImage->height-0.5f)*(bottom-top);
#else
	tx=(contact->bx/bodyImage->width-0.5f)*(right-left);
	ty=(contact->by/bodyImage->height-0.5f)*(bottom-top);
#endif
	extra=stock->angle-base->angle;
	if(!rotate_extra(&tx,&ty,extra)) return 0;
	cx=(left+right)*0.5f+tx; cy=(top+bottom)*0.5f+ty;
	mirror=(l->mirror!=0)^(r->mirrorXor!=0);
	/* Keep the accepted rig angle; contact placement must not rotate the blade. */
	angle=(float)r->angle+extra;
	w=im->width*sx; h=im->height*sy;
	if(!positive(w,32768) || !positive(h,32768)) return 0;
#ifdef DW_MEASURE_CONTACTS
	tx=(grip->gx+0.5f-im->width*0.5f)*(mirror?-sx:sx);
	ty=(grip->gy+0.5f-im->height*0.5f)*sy;
#else
	tx=(contact->wx-im->width*0.5f)*(mirror?-sx:sx);
	ty=(contact->wy-im->height*0.5f)*sy;
#endif
	if(!rotate_extra(&tx,&ty,angle)) return 0;
	cx-=tx; cy-=ty;
	for(i=0;i<12;i++) ((u32 *)&out->packet)[i]=((u32 *)stock)[i];
	out->packet.left=cx+(mirror?w:-w)*0.5f;
	out->packet.right=cx+(mirror?-w:w)*0.5f;
	out->packet.top=cy-h*0.5f; out->packet.bottom=cy+h*0.5f;
	out->packet.angle=angle; out->packet.image=im;
	out->palette=(void *)(spr+0x110); out->visible=1;
	return 1;
}

static int prepare_reference(Prepared *out,Packet *stock,Layer *base,
	u32 spr,u32 act,const DWNativeBasis *basis,int hand,int dir)
{
	const DWNativeGuide *g=&basis->guide;
	const DWNativeReferenceHand *r=&basis->hands[hand];
	Layer *l;
	Image *im;
	float sw,sh,sx,sy,ox,oy,left,right,top,bottom,ux,uy,cx,cy,dx,dy,w,h,tx,ty;
	u32 frames,layerEnd,layerBytes;
	int i,action,mirror;
	out->visible=0; out->order=r->order;
	if(r->hidden) return 1;
	action=(r->sourceAttack?80:32)+dir;
	l=layer_at(act,action,r->sourceFrame);
	im=image_at(spr,l);
	if(!im || !stock->image || !base || !g->channel || !g->width || !g->height) return 0;
	if(im->columns || im->rows || stock->image->columns<0 || stock->image->rows<0 ||
		stock->image->columns>16 || stock->image->rows>16 ||
		!positive(base->sx,16) || !positive(base->sy,16)) return 0;
	/* Axis scaling followed by a new nonzero source rotation can require
	 * shear. Only zero source angles have a verified rectangular contract.
	 * Positive finite native scale and source mirroring remain independent. */
	if(l->angle || r->sourceAngle || r->sourceLayer ||
		!positive(l->sx,16) || !positive(l->sy,16) ||
		!positive(r->sx,16) || !positive(r->sy,16)) return 0;
	/* This helper emits one selected original layer. Refuse another real
	 * image in the exact frame rather than silently lose multi-layer art.
	 * Treat an alpha-zero extra image conservatively as requiring that path. */
	frames=rd(rd(act,0x110),action*12);
	layerEnd=rd(frames+r->sourceFrame*68,0x24);
	layerBytes=layerEnd-(u32)l;
	if(layerBytes%36) return 0;
	for(i=1;i<(int)(layerBytes/36);i++)
		if(image_at(spr,l+i)) return 0;
	sw=(float)(stock->image->width*(stock->image->columns+1));
	sh=(float)(stock->image->height*(stock->image->rows+1));
	if(!positive(sw,32768) || !positive(sh,32768)) return 0;
	sx=absolute(stock->right-stock->left-1)/(sw*base->sx);
	sy=absolute(stock->bottom-stock->top-1)/(sh*base->sy);
	if(!positive(sx,64) || !positive(sy,64)) return 0;
	ox=stock->left-(base->x+(base->mirror?sw:0))*sx*base->sx;
	oy=stock->top-base->y*sy*base->sy;
	left=ox+(g->x+(g->mirror?g->width:0))*sx*g->sx;
	right=ox+(g->x+(g->mirror?0:g->width))*sx*g->sx+1;
	top=oy+g->y*sy*g->sy;
	bottom=oy+(g->y+g->height)*sy*g->sy+1;
	ux=absolute(right-left)/(g->width*absolute(g->sx));
	uy=absolute(bottom-top)/(g->height*absolute(g->sy));
	dx=(float)r->dx; dy=(float)r->dy;
	if(!r->packetDelta) { dx+=r->sourceX-g->x; dy+=r->sourceY-g->y; }
	cx=(left+right)*0.5f+dx*ux; cy=(top+bottom)*0.5f+dy*uy;
	/* Native image-center registration is resource-specific, not a weapon
	 * type delta. Keep half-pixel parity, each source's scale, and the
	 * source ACT's own mirror. Only the extra reference mirror reflects
	 * this displacement again. Axis scales must precede final rotation. */
	tx=((float)l->x+im->width*0.5f)*l->sx-
		((float)r->sourceX+r->width*0.5f)*r->sx;
	ty=((float)l->y+im->height*0.5f)*l->sy-
		((float)r->sourceY+r->height*0.5f)*r->sy;
	if(r->mirrorXor) tx=-tx;
	tx*=ux; ty*=uy;
	if(!rotate_extra(&tx,&ty,(float)r->angle+stock->angle-base->angle)) return 0;
	cx+=tx; cy+=ty;
	mirror=(l->mirror!=0)^(r->mirrorXor!=0);
	w=im->width*absolute(l->sx)*ux; h=im->height*absolute(l->sy)*uy;
	if(!positive(w,32768) || !positive(h,32768)) return 0;
	for(i=0;i<12;i++) ((u32 *)&out->packet)[i]=((u32 *)stock)[i];
	out->packet.left=cx+(mirror?w:-w)*0.5f;
	out->packet.right=cx+(mirror?-w:w)*0.5f;
	out->packet.top=cy-h*0.5f; out->packet.bottom=cy+h*0.5f;
	out->packet.angle=stock->angle-base->angle+(float)(l->angle+r->angle);
	out->packet.image=im; out->palette=(void *)(spr+0x110); out->visible=1;
	return 1;
}

/* The reference body timeline is female Assassin-family only. CResource
 * stores its native CP949 filename inline at +0x14. Gender alone admits other
 * jobs with unrelated hand positions; require both retained hand ACT families.
 * This is a family scope check, not proof that missing item art exists. */
#include "male_compositor.h"
#include "female_dagger_compositor.h"
#include "female_family_compositor.h"
static int supported_type(u32 type) { return type==1 || type==2 || type==6; }
static int reference_family(u32 act)
{
	static const u8 prefix[]="\x73\x70\x72\x69\x74\x65\x5c\xc0\xce\xb0\xa3\xc1\xb7\x5c\xbe\xee\xbc\xbc\xbd\xc5\x5c\xbe\xee\xbc\xbc\xbd\xc5\x5f\xbf\xa9\x5f";
	static const u8 shadow[]="sprite\\\xc0\xce\xb0\xa3\xc1\xb7\\shadow_cross\\shadow_cross_\xbf\xa9_";
	const u8 *name=(const u8 *)(act+0x14);
	u32 i;
	if(!act) return 0;
	for(i=0;i<sizeof(prefix)-1;i++) if(name[i]!=prefix[i]) break;
	if(i==sizeof(prefix)-1) return 1;
	for(i=0;i<sizeof(shadow)-1;i++) if(name[i]!=shadow[i]) return 0;
	return 1;
}

/* Context retains its 21-DWORD ABI; retired legacy slots are reserved zero.
 * [18] is the actor view-pair registry. Placement tables are compiled below.
 * Resource identity is resolved from THIS actor's restored stock resources
 * and current ACT frame, never the global last-image/recent-capture ring. */
extern "C" __declspec(dllexport) int __stdcall DualWeaponCompose(void *actor,Packet *packet,
	void *palette,u32 a3,float a4,float a5,u32 a6,u32 *ctx,Draw draw)
{
	u32 ap=(u32)actor,sv,se,av,ae,bodyAct,stockSpr[2],views;
	Row *row;
	Layer *base[2],*body;
	Image *image[2],*bodyImage;
	int action,frame,channel=-1,i,phase,dir,hand,offOnly,sourceFrame,bi;
	u32 spr[2],act[2];
	const DWNativeBasis *basis;
	const DWBodyGrip *socket;
	Prepared hands[2];
	if(!actor || !packet || !ctx || !draw || !ctx[0]) return 0;
	row=(Row *)(ctx[0]+((ap>>4)&255)*60);
	if(row->actor!=ap || !row->offSpr || !row->offAct) return 0;
	offOnly=rd(ap,ctx[11])==0;
	if(!rd(ap,ctx[12]) || (!offOnly && (!row->mainSpr || !row->mainAct))) return 0;
	if(row->gender==1) return compose_male(actor,packet,palette,a3,a4,a5,a6,ctx,draw,row,offOnly);
	if(row->gender!=0 || !supported_type(row->offType) ||
		!reference_family(row->offAct) || (!offOnly &&
		(!supported_type(row->mainType) || !reference_family(row->mainAct)))) return 0;
	action=rd(ap,ctx[5]); frame=rd(ap,ctx[6]);
	sv=rd(ap,0x4AC); se=rd(ap,0x4B0);
	if(!sv || se<sv || se-sv<28) return 0;
	for(i=0;i<2;i++) {
		stockSpr[i]=rd(sv,20+i*4);
		base[i]=layer_at(i?row->stockTrailAct:row->stockAct,action,frame);
		image[i]=image_at(stockSpr[i],base[i]);
		if(image[i] && image[i]==packet->image && palette==(void *)(stockSpr[i]+0x110)) {
			if(channel!=-1) return 0;
			channel=i;
		}
	}
	if(channel<0) return 0;
	/* Other native phases retain their inherited resource path. Their body
	 * timelines are not silently reinterpreted as held32 or dual88. */
	if(offOnly && !(action>=32 && action<40 && frame>=0 && frame<6)) {
		spr[0]=channel?row->offTrailSpr:row->offSpr;
		act[0]=channel?row->offTrailAct:row->offAct;
		sourceFrame=layer_at(act[0],action,frame)?frame:0;
		if(!prepare(&hands[0],packet,base[channel],spr[0],act[0],action,sourceFrame,0,0)) return 0;
		if(hands[0].visible) draw(actor,&hands[0].packet,hands[0].palette,a3,a4,a5,a6);
		return 1;
	}
	if(action>=32 && action<40 && frame>=0 && frame<6) { phase=0; dir=action-32; }
	else if(action>=88 && action<96 && frame>=0 && frame<8) { phase=1; dir=action-88; }
	else return 0;
	views=ctx[18]?ctx[18]+((ap>>4)&255)*8:0;
	if(!views || !profiled_view(rd(views,4)) || (!offOnly && !profiled_view(rd(views,0)))) return 0;
	av=rd(ap,0x4B8); ae=rd(ap,0x4BC);
	if(!av || ae<av || ae-av<4 || ae-av>64) return 0;
	bodyAct=rd(av,0); bi=female_body(bodyAct,rd(sv,0)); if(bi<0) return 0;
	body=layer_at(bodyAct,action,frame); bodyImage=image_at(rd(sv,0),body);
	socket=&DW_BODY_GRIPS[phase][dir][frame];
	if(!male_fingerprint(body,bodyImage,&DWFF_BODIES[bi][phase][dir][frame])) return 0;
	if(bi==2 && (!body_family(bodyAct,0) || !body_family(rd(sv,0),1) || body->kind || body->index!=socket->index ||
		body->x!=socket->x || body->y!=socket->y || body->mirror!=socket->mirror ||
		body->sx!=1 || body->sy!=1 || body->angle ||
		bodyImage->width!=socket->width || bodyImage->height!=socket->height)) return 0;
	basis=&DW_NATIVE_BASIS[phase][dir][frame];
	if(offOnly) {
		hand=1-socket->mainHand;
		if(bi!=2 || (rd(views,4)>=58 && rd(views,4)<=61)) {
			if(!female_family_prepare(&hands[0],packet,base[channel],row->offSpr,row->offAct,
				rd(views,4),bi,body,bodyImage,basis,phase,dir,frame,hand)) return 0;
		} else if(rd(views,4)>=31 && rd(views,4)<=33) {
			if(row->offType!=1 || !female_dagger_prepare(&hands[0],packet,base[channel],row->offSpr,row->offAct,
				rd(views,4),body,bodyImage,basis,phase,dir,frame,hand)) return 0;
		} else if(!prepare_gripped(&hands[0],packet,base[channel],row->offSpr,row->offAct,
			rd(views,4),body,bodyImage,basis,hand,dir,frame)) return 0;
		if(channel==1 && image[0]) return 1;
		if(hands[0].visible) draw(actor,&hands[0].packet,hands[0].palette,a3,a4,a5,a6);
		return 1;
	}
	/* Slots are anatomical ownership. The same source body images are
	 * mirrored by the native ACT in opposite directions, so the anatomical
	 * right arm is not always reference role0. Never sort by weapon class.
	 * The legacy ctx19 entry remains in the ABI but cannot bypass grips. */
	spr[0]=row->mainSpr; act[0]=row->mainAct;
	spr[1]=row->offSpr; act[1]=row->offAct;
	for(i=0;i<2;i++) {
		hand=i?1-socket->mainHand:socket->mainHand;
		if(bi!=2 || (rd(views,i*4)>=58 && rd(views,i*4)<=61)) {
			if(!female_family_prepare(&hands[i],packet,base[channel],spr[i],act[i],
				rd(views,i*4),bi,body,bodyImage,basis,phase,dir,frame,hand)) return 0;
		} else if(rd(views,i*4)>=31 && rd(views,i*4)<=33) {
			if((i?row->offType:row->mainType)!=1 || !female_dagger_prepare(&hands[i],packet,base[channel],spr[i],act[i],
				rd(views,i*4),body,bodyImage,basis,phase,dir,frame,hand)) return 0;
		} else if(phase==1) {
			/* Attack guides include intentional detached slash art. Preserve the
			 * documented packet positions, source frames and angles; no palm snap. */
			if(!prepare_reference(&hands[i],packet,base[channel],spr[i],act[i],basis,hand,dir)) return 0;
		} else if(!prepare_gripped(&hands[i],packet,base[channel],spr[i],act[i],rd(views,i*4),
			body,bodyImage,basis,hand,dir,frame)) return 0;
	}
	if(channel==1 && image[0]) return 1;
	if(hands[0].order>hands[1].order) {
		if(hands[1].visible) draw(actor,&hands[1].packet,hands[1].palette,a3,a4,a5,a6);
		if(hands[0].visible) draw(actor,&hands[0].packet,hands[0].palette,a3,a4,a5,a6);
	} else {
		if(hands[0].visible) draw(actor,&hands[0].packet,hands[0].palette,a3,a4,a5,a6);
		if(hands[1].visible) draw(actor,&hands[1].packet,hands[1].palette,a3,a4,a5,a6);
	}
	return 1;
}
extern "C" { int _fltused=0; }
