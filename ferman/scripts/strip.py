import cv2,numpy as np,sys,math
im=np.load('/workspace/home/work/r.npy',mmap_mode='r')
name=sys.argv[1]; xr,yr=map(float,sys.argv[2].split(',')); xl,yl=map(float,sys.argv[3].split(','))
up=int(sys.argv[4]) if len(sys.argv)>4 else 520; dn=int(sys.argv[5]) if len(sys.argv)>5 else 280
nseg=int(sys.argv[6]) if len(sys.argv)>6 else 3
L=math.hypot(xl-xr,yl-yr); ux,uy=(xl-xr)/L,(yl-yr)/L  # along line (to the left)
nx,ny=-uy,ux
# normal pointing down? ensure ny>0
if ny<0: nx,ny=-nx,-ny
y0=int(max(0,min(yr,yl)-up-50)); y1=int(min(im.shape[0],max(yr,yl)+dn+50)); x0=int(max(0,min(xr,xl)-50)); x1=int(min(im.shape[1],max(xr,xl)+50))
sub=np.ascontiguousarray(im[y0:y1,x0:x1])
u=np.arange(0,L,dtype=np.float32); v=np.arange(-up,dn,dtype=np.float32)
U,V=np.meshgrid(u,v)
mx=(xr+U*ux+V*nx-x0).astype(np.float32); my=(yr+U*uy+V*ny-y0).astype(np.float32)
st=cv2.remap(sub,mx,my,cv2.INTER_LINEAR,borderValue=(255,255,255))
n=nseg; seglen=int(np.ceil(L/n)); ov=150
parts=[]
for i in range(n):
    a=max(0,i*seglen-ov); b=min(st.shape[1],(i+1)*seglen)
    seg=st[:,a:b][:,::-1]  # right-to-left reading order: segment i covers u from a..b, flip back to image orientation
    seg=seg[:,::-1]
    # u increases leftwards in the image; so image orientation = reversed u
    seg=st[:,a:b][:,::-1]
    s=1040/seg.shape[1]
    cv2.imwrite(f'/workspace/home/work/{name}_{i}.jpg',cv2.resize(seg,None,fx=s,fy=s,interpolation=cv2.INTER_AREA),[cv2.IMWRITE_JPEG_QUALITY,90])
    parts.append(f'<img src="{name}_{i}.jpg" style="display:block;margin-bottom:6px">')
for pi in range(0,len(parts),3):
    open(f'/workspace/home/work/{name}{chr(97+pi//3)}.html','w').write('<body style="margin:0;background:#666">'+''.join(parts[pi:pi+3])+'</body>')
print('ok',int(L))
