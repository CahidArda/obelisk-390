import cv2,numpy as np,sys
from PIL import Image,ImageOps
rep=np.load('/workspace/home/work/r.npy',mmap_mode='r')
def ymap(img,sig=20):
    b=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,2].astype(np.float32)
    h=np.clip(b-cv2.GaussianBlur(b,(0,0),sig),0,None); return cv2.GaussianBlur(h,(0,0),2.5)
def dmap(img,sig=20):
    L=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(np.float32)
    h=np.clip(cv2.GaussianBlur(L,(0,0),sig)-L,0,None); return cv2.GaussianBlur(h,(0,0),2.5)
n=sys.argv[1] if len(sys.argv)>1 else 'IMG_4234'
Pr=np.float32([[3802,685],[3414,1472],[4794,1376],[4453,1536],[3862,1386]])
Pp={'IMG_4234':np.float32([[877,1192],[406,2354],[2098,1747],[1681,2086],[885,2030]])}[n]
X0,Y0,X1,Y1=3300,450,5000,1650
R=np.ascontiguousarray(rep[Y0:Y1,X0:X1]); rb=ymap(R); rb/=np.percentile(rb,99.5)
im=np.array(ImageOps.exif_transpose(Image.open(f'/workspace/home/uploads2/{n}.jpeg')).convert('RGB'))[:,:,::-1].copy()
H0,_=cv2.findHomography(Pp,Pr,0)
T=np.array([[1,0,-X0],[0,1,-Y0],[0,0,1]],float)
H=H0.copy()
np.save(f'/workspace/home/work/Hg_{n}.npy',H)
for tag,HH in [('init',H0),('ecc',H)]:
    w=cv2.warpPerspective(im,T@HH,(X1-X0,Y1-Y0)); b=dmap(w); b/=np.percentile(b,99.5)
    ov=np.zeros_like(R); ov[...,2]=np.clip(rb*200,0,255); ov[...,1]=np.clip(b*200,0,255)
    cv2.imwrite(f'/workspace/home/work/ovm_{tag}.jpg',cv2.resize(ov,None,fx=.6,fy=.6))

# ---- block matching refinement ----
H=H0.copy()
for it,(P,Srch) in enumerate([(220,160),(160,70),(120,35)]):
    w=cv2.warpPerspective(im,T@H,(X1-X0,Y1-Y0)); wb=dmap(w); wb/=np.percentile(wb,99.5)
    A=rb.astype(np.float32); B=wb.astype(np.float32)
    src=[];dst=[]
    for y in range(Srch,A.shape[0]-P-Srch,P//2):
        for x in range(Srch,A.shape[1]-P-Srch,P//2):
            patch=A[y:y+P,x:x+P]
            if patch.mean()<0.06: continue
            win=B[y-Srch:y+P+Srch,x-Srch:x+P+Srch]
            r=cv2.matchTemplate(win,patch,cv2.TM_CCOEFF_NORMED)
            _,mx,_,loc=cv2.minMaxLoc(r)
            if mx<0.3: continue
            dx,dy=loc[0]-Srch,loc[1]-Srch
            dst.append([x+P/2,y+P/2]); src.append([x+P/2+dx,y+P/2+dy])
    src=np.float32(src); dst=np.float32(dst)
    # src: point in warped-photo frame; dst: replica frame. correction C maps warped->replica
    C,mk=cv2.findHomography(src,dst,cv2.RANSAC,6.0)
    print('iter',it,'pairs',len(src),'inliers',int(mk.sum()))
    Tinv=np.linalg.inv(T)
    H=Tinv@C@T@H
np.save(f'/workspace/home/work/Hg_{n}.npy',H)
w=cv2.warpPerspective(im,T@H,(X1-X0,Y1-Y0)); b=dmap(w); b/=np.percentile(b,99.5)
ov=np.zeros_like(R); ov[...,2]=np.clip(rb*200,0,255); ov[...,1]=np.clip(b*200,0,255)
cv2.imwrite('/workspace/home/work/ovm_ecc.jpg',cv2.resize(ov,None,fx=.6,fy=.6))
