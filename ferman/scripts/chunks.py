import cv2,numpy as np,json
im=np.load('/workspace/home/work/r.npy',mmap_mode='r')
k=4
sm=cv2.resize(np.ascontiguousarray(im),None,fx=1/k,fy=1/k,interpolation=cv2.INTER_AREA).astype(np.int16)
b,g,r=sm[...,0],sm[...,1],sm[...,2]
L=(b+g+r)/3
bg=cv2.medianBlur(L.astype(np.uint8),51).astype(np.int16)
ink=((L<bg-28)|((r-g)>40)).astype(np.uint8)
ink=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(ink,8)
P={
 'l1':[(7100,9817),(900,9150),(450,8700)],
 'l2':[(7100,10950),(900,10033),(650,9550)],
 'l3':[(7100,12150),(900,11033),(620,10480)],
 'l4':[(7100,13367),(950,12033),(650,11460)],
 'l5':[(7100,14550),(950,13117),(600,12330)],
 'l6':[(7100,15533),(950,13867),(550,13400)],
 'l7':[(7100,16700),(950,15033),(550,14600)],
 'nisan':[(2950,8420),(450,8330),(300,8050)],
}
BOX={'tugra':(2900,6000,6300,8450),'place':(350,15050,1850,16650),'davet':(3300,500,4400,1450)}
def segd(p,a,b):
    p=np.asarray(p,float);a=np.asarray(a,float);b=np.asarray(b,float)
    ab=b-a;t=np.clip(((p-a)@ab)/(ab@ab),0,1);return np.linalg.norm(p-(a+t*ab))
def dist(p,pl): return min(segd(p,pl[i],pl[i+1]) for i in range(len(pl)-1))
assign={key:[] for key in list(P)+list(BOX)}
for i in range(1,n):
    x,y,w,h,a=st[i]
    if a<6: continue
    X,Y=(x+w/2)*k,(y+h/2)*k
    if (w>10*h and h*k<90) or (w*k>1500 and a<w*3): continue  # creases
    hit=None
    for key,(x0,y0,x1,y1) in BOX.items():
        if x0<=X<=x1 and y0<=Y<=y1: hit=key
    if hit is None:
        # weight: text sits ~200px below anchor lines
        ds={key:dist((X,Y-200),pl) for key,pl in P.items()}
        key=min(ds,key=ds.get)
        if ds[key]<520: hit=key
    if hit: assign[hit].append(i)
import math
opened=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
CLIP={'l1':6750,'l2':6800,'l3':7150,'l4':6750,'l5':6750,'l6':6800,'l7':6750,'nisan':3700}
out={}
keep=json.load(open('/workspace/home/work/regions_final.json'))
GAP=110//k   # gap between word groups (full-res px)
MINW=260//k; MAXW=1300//k
def rrect(pts,pad):
    # robust oriented box: PCA frame, trimmed percentiles
    c=pts.mean(0); u,sv,vt=np.linalg.svd(pts-c,full_matrices=False); ax=vt[0]
    if abs(ax[0])<abs(ax[1]) and len(pts)<10: ax=np.array([1.0,0.0])
    if ax[0]<0: ax=-ax
    nx=np.array([-ax[1],ax[0]])
    a=(pts-c)@ax; b=(pts-c)@nx
    a0,a1=np.percentile(a,[1,99]); b0,b1=np.percentile(b,[4,96])
    a0-=pad;a1+=pad;b0-=pad;b1+=pad
    r=min(pad*1.4,(a1-a0)/2,(b1-b0)/2); poly=[]
    for (ca,cb,st) in [(a1-r,b0+r,-90),(a1-r,b1-r,0),(a0+r,b1-r,90),(a0+r,b0+r,180)]:
        for d in range(st,st+91,30):
            t=math.radians(d); pa=ca+r*math.cos(t); pb=cb+r*math.sin(t)
            p=c+pa*ax+pb*nx; poly.append([int(p[0]*k),int(p[1]*k)])
    return poly
for key,ids in assign.items():
    if key in BOX:
        out[key]=keep[key]; continue
    pl=P[key]
    comps=[]
    for i in ids:
        x,y,w,h,a=st[i]
        ys,xs=np.nonzero((lab[y:y+h,x:x+w]==i)&(opened[y:y+h,x:x+w]>0))
        keepm=(xs+x)*k<=CLIP.get(key,99999)
        ys,xs=ys[keepm],xs[keepm]
        if len(xs)<4: continue
        pts=np.stack([xs+x,ys+y],1).astype(float)
        comps.append((x,x+w,pts))
    comps.sort(key=lambda c:-c[1])  # right to left (reading order)
    groups=[];cur=None
    for x0,x1,pts in comps:
        if cur and (cur['x0']-x1)<GAP and (cur['x1']-x0)<MAXW:
            cur['x0']=min(cur['x0'],x0);cur['pts'].append(pts)
        else:
            cur={'x0':x0,'x1':x1,'pts':[pts]};groups.append(cur)
    # merge too-small groups into neighbour
    changed=True
    while changed and len(groups)>1:
        changed=False
        for gi,g in enumerate(groups):
            if g['x1']-g['x0']<MINW:
                j=gi-1 if gi>0 else gi+1
                o=groups[j]; o['x0']=min(o['x0'],g['x0']);o['x1']=max(o['x1'],g['x1']);o['pts']+=g['pts']
                groups.pop(gi);changed=True;break
    groups=[g for g in groups if sum(len(p) for p in g['pts'])>=150]
    polys=[rrect(np.concatenate(g['pts']),7) for g in groups]
    xs=[p[0] for q in polys for p in q]; ys=[p[1] for q in polys for p in q]
    out[key]={'polys':polys,'bbox':[min(xs),min(ys),max(xs),max(ys)]}
    print(key,len(polys),'chunks',out[key]['bbox'])
json.dump(out,open('/workspace/home/work/regions_chunks.json','w'))
prev=cv2.resize(np.ascontiguousarray(im),None,fx=0.06,fy=0.06,interpolation=cv2.INTER_AREA)
for j,(key,v) in enumerate(out.items()):
    for q in v['polys']:
        cv2.polylines(prev,[(np.array(q)*0.06).astype(np.int32)],True,[(200,0,0),(0,140,0),(0,0,220),(180,0,180)][j%4],1,cv2.LINE_AA)
cv2.imwrite('/workspace/home/work/chunks.png',prev)
