from common import *
import sys
WS=0.25  # working scale of canvas
ref=load('IMG_4203.jpeg')
Hr=cv2.getPerspectiveTransform(QUAD,canvas_quad(WS))
rw,rh=int(CW*WS),int(CH*WS)
refw=cv2.warpPerspective(ref,Hr,(rw,rh),flags=cv2.INTER_CUBIC)
cv2.imwrite(W+'/ref_work.jpg',refw)
rg=gray(refw)
sift=cv2.SIFT_create(nfeatures=40000)
kr,dr=sift.detectAndCompute(rg,None)
print('ref kp',len(kr),flush=True)
matcher=cv2.FlannBasedMatcher(dict(algorithm=1,trees=5),dict(checks=64))
res={}
for f in sorted(os.listdir(UP)):
    if f in ('IMG_4203.jpeg','IMG_4205.jpeg') or not f.endswith('.jpeg'): continue
    im=load(f); g0=gray(im); best=None
    for L in [500,750,1100,1600,2300]:
        s=L/max(g0.shape)
        g=cv2.resize(g0,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
        k,d=sift.detectAndCompute(g,None)
        if d is None or len(k)<10: continue
        ms=matcher.knnMatch(d,dr,k=2)
        good=[m for m,n in ms if m.distance<0.75*n.distance]
        if len(good)<12: continue
        src=np.float32([k[m.queryIdx].pt for m in good])/s
        dst=np.float32([kr[m.trainIdx].pt for m in good])
        H,mask=cv2.findHomography(src,dst,cv2.USAC_MAGSAC,4.0,maxIters=20000,confidence=0.999)
        if H is None: continue
        ni=int(mask.sum())
        if best is None or ni>best[0]: best=(ni,L,H,len(good))
    if best:
        ni,L,H,ng=best
        h,w=g0.shape
        corners=cv2.perspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2),H).reshape(-1,2)
        # local scale: canvas px per photo px at center
        c=cv2.perspectiveTransform(np.float32([[[w/2,h/2]],[[w/2+1,h/2]]]),H).reshape(-1,2)
        sc=float(np.linalg.norm(c[1]-c[0]))
        res[f]=dict(H=H.tolist(),inl=ni,good=ng,L=L,scale=sc)
        print(f,'inliers',ni,'/',ng,'L',L,'canvas_px_per_photo_px(work)',round(sc,4),'corners',corners.round().tolist(),flush=True)
    else:
        print(f,'FAILED',flush=True)
json.dump(res,open(W+'/H_work.json','w'))
print('DONE',flush=True)
