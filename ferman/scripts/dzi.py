import os,math
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
src=Image.open('/workspace/home/work/replica.png').convert('RGB')
W,H=src.size; T=510; O=1
out='/workspace/home/work/dzi/replica_files'; os.makedirs(out,exist_ok=True)
maxL=math.ceil(math.log2(max(W,H)))
img=src
n=0
for L in range(maxL,-1,-1):
    s=2**(maxL-L); w=max(1,math.ceil(W/s)); h=max(1,math.ceil(H/s))
    if (w,h)!=img.size: img=img.resize((w,h),Image.LANCZOS)
    d=f'{out}/{L}'; os.makedirs(d,exist_ok=True)
    for ty in range(math.ceil(h/T)):
        for tx in range(math.ceil(w/T)):
            x0=max(0,tx*T-O); y0=max(0,ty*T-O); x1=min(w,(tx+1)*T+O); y1=min(h,(ty+1)*T+O)
            img.crop((x0,y0,x1,y1)).save(f'{d}/{tx}_{ty}.jpg',quality=84,optimize=True,progressive=True); n+=1
    print('level',L,w,h,flush=True)
open('/workspace/home/work/dzi/replica.dzi','w').write(f'<?xml version="1.0" encoding="UTF-8"?><Image xmlns="http://schemas.microsoft.com/deepzoom/2008" TileSize="{T}" Overlap="{O}" Format="jpg"><Size Width="{W}" Height="{H}"/></Image>')
print('DONE tiles',n,flush=True)
