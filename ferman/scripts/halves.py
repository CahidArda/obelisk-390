import cv2,numpy as np,json,math,sys,os
im=np.load('/workspace/home/work/r.npy',mmap_mode='r')
src=open('/workspace/home/obelisk-390/ferman/data.js').read()
D=json.loads(src[src.index('=')+1:].strip().rstrip(';'))
W='/workspace/home/work/halves'; os.makedirs(W,exist_ok=True)
def straight(P,pad=50):
    c=P.mean(0); u,s,vt=np.linalg.svd(P-c); ax=vt[0]
    if ax[0]<0: ax=-ax
    ang=math.degrees(math.atan2(ax[1],ax[0]))
    x0,y0=np.maximum(P.min(0)-pad,0).astype(int); x1,y1=(P.max(0)+pad).astype(int)
    crop=np.ascontiguousarray(im[y0:y1,x0:x1])
    if abs(ang)<35:
        h,w=crop.shape[:2]; M=cv2.getRotationMatrix2D((w/2,h/2),ang,1.0)
        cs,sn=abs(M[0,0]),abs(M[0,1]); nw,nh=int(w*cs+h*sn),int(w*sn+h*cs); M[0,2]+=nw/2-w/2; M[1,2]+=nh/2-h/2
        crop=cv2.warpAffine(crop,M,(nw,nh),borderValue=(235,235,235))
        Q=cv2.transform((P-[x0,y0]).reshape(-1,1,2),M).reshape(-1,2)
        qx0,qy0=np.maximum(Q.min(0)-20,0).astype(int); qx1,qy1=(Q.max(0)+20).astype(int)
        crop=crop[qy0:qy1,qx0:qx1]
    return crop
for key in sys.argv[1:]:
    parts=[]
    for i,p in enumerate(D['regions'][key]['polys']):
        cr=straight(np.array(p,np.float32))
        h,w=cr.shape[:2]
        segs=[(0,w)] if w<700 else [(w//2-80,w),(0,w//2+80)]  # right half first (reading order)
        for j,(a,b) in enumerate(segs):
            s=cr[:,a:b]; sc=min(1.8,1040/s.shape[1],900/s.shape[0])
            s=cv2.resize(s,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
            g=cv2.cvtColor(s,cv2.COLOR_BGR2LAB); l=g[...,0]; g[...,0]=cv2.createCLAHE(2.0,(8,8)).apply(l); s=cv2.cvtColor(g,cv2.COLOR_LAB2BGR)
            fn=f'{key}_{i}_{j}.jpg'; cv2.imwrite(f'{W}/{fn}',s,[cv2.IMWRITE_JPEG_QUALITY,92])
            parts.append((i,j,fn))
    for k in range(0,len(parts),3):
        html=''.join(f'<div style="font:13px sans-serif;color:#c00;margin:3px 0">{key} box {i} {"right" if j==0 else "left"}</div><img src="{fn}" style="display:block">' for i,j,fn in parts[k:k+3])
        open(f'{W}/{key}_p{k//3}.html','w').write('<body style="margin:0">'+html+'</body>')
    print(key,len(parts),'crops',(len(parts)+2)//3,'pages')
