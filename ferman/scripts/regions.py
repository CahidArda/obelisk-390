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
out={}
for key,ids in assign.items():
    m=np.isin(lab,ids)
    if key in BOX:
        x0,y0,x1,y1=[v//k for v in BOX[key]]
        mm=np.zeros_like(m); mm[y0:y1,x0:x1]=m[y0:y1,x0:x1]
        pts=cv2.findNonZero(mm.astype(np.uint8))
        hull=cv2.convexHull(pts).reshape(-1,2)
        poly=(hull*k).astype(int).tolist()
    else:
        ys,xs=np.nonzero(m)
        B=25; top=[];bot=[];cx=[]
        for bx in range(xs.min()//B,xs.max()//B+1):
            sel=ys[(xs>=bx*B)&(xs<(bx+1)*B)]
            if len(sel)<70: continue
            cx.append(bx*B+B/2); top.append(np.percentile(sel,2)-12); bot.append(np.percentile(sel,98)+12)
        top=np.array(top);bot=np.array(bot)
        from scipy.ndimage import median_filter
        top=median_filter(top,9,mode="nearest");bot=median_filter(bot,9,mode="nearest");from scipy.ndimage import gaussian_filter1d;top=gaussian_filter1d(np.minimum.accumulate(top[::-1])[::-1]*0+top,1.5);bot=gaussian_filter1d(bot,1.5)
        cx=np.array(cx); cx[0]-=B/2; cx[-1]+=B/2
        poly=[[int(x*k),int(y*k)] for x,y in zip(cx,top)]+[[int(x*k),int(y*k)] for x,y in zip(cx[::-1],bot[::-1])]
    xs_=[p[0] for p in poly]; ys_=[p[1] for p in poly]
    out[key]={'polys':[poly],'bbox':[min(xs_),min(ys_),max(xs_),max(ys_)]}
    print(key,out[key]['bbox'],len(poly))
json.dump(out,open('/workspace/home/work/regions.json','w'))
prev=cv2.resize(np.ascontiguousarray(im),None,fx=0.06,fy=0.06,interpolation=cv2.INTER_AREA)
cols=[(255,0,0),(0,150,0),(0,0,255),(200,0,200),(0,160,160),(160,100,0),(80,80,255),(0,0,0),(120,120,0),(0,90,180),(180,0,90)]
for j,(key,v) in enumerate(out.items()):
    for pl in v['polys']:
        cv2.polylines(prev,[(np.array(pl)*0.06).astype(np.int32)],True,cols[j%len(cols)],1)
cv2.imwrite('/workspace/home/work/regions.png',prev)
