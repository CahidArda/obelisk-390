import cv2,numpy as np,json,math
im=np.load('/workspace/home/work/r.npy',mmap_mode='r')
src=open('/workspace/home/obelisk-390/ferman/data.js').read()
D=json.loads(src[src.index('=')+1:].strip().rstrip(';'))
W='/workspace/home/work/boxes'; import os; os.makedirs(W,exist_ok=True)
for key in ['nisan','l1','l2','l3','l4','l5','l6','l7']:
    parts=[]
    for i,p in enumerate(D['regions'][key]['polys']):
        P=np.array(p,np.float32)
        c=P.mean(0); u,s,vt=np.linalg.svd(P-c); ax=vt[0]
        if ax[0]<0: ax=-ax
        ang=math.degrees(math.atan2(ax[1],ax[0]))
        pad=60
        x0,y0=P.min(0)-pad; x1,y1=P.max(0)+pad
        x0,y0=max(0,int(x0)),max(0,int(y0)); x1,y1=min(im.shape[1],int(x1)),min(im.shape[0],int(y1))
        crop=np.ascontiguousarray(im[y0:y1,x0:x1])
        if abs(ang)<35:
            # rotate to horizontal around center, keep full content
            h,w=crop.shape[:2]; M=cv2.getRotationMatrix2D((w/2,h/2),ang,1.0)
            cs,sn=abs(M[0,0]),abs(M[0,1]); nw,nh=int(w*cs+h*sn),int(w*sn+h*cs)
            M[0,2]+=nw/2-w/2; M[1,2]+=nh/2-h/2
            crop=cv2.warpAffine(crop,M,(nw,nh),borderValue=(235,235,235))
            # trim to the box's rotated extent
            Q=cv2.transform((P-[x0,y0]).reshape(-1,1,2),M).reshape(-1,2)
            qx0,qy0=np.maximum(Q.min(0)-30,0).astype(int); qx1,qy1=(Q.max(0)+30).astype(int)
            crop=crop[qy0:qy1,qx0:qx1]
        sc=min(1.2,1040/crop.shape[1],700/crop.shape[0])
        crop=cv2.resize(crop,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
        fn=f'{key}_{i}.jpg'; cv2.imwrite(f'{W}/{fn}',crop,[cv2.IMWRITE_JPEG_QUALITY,92])
        parts.append(f'<div style="font:13px sans-serif;color:#c00;margin:4px 0 2px">{key} box {i}  angle {ang:.0f}</div><img src="{fn}" style="display:block">')
    open(f'{W}/{key}.html','w').write('<body style="margin:0;background:#fff">'+''.join(parts)+'</body>')
    print(key,len(parts))
