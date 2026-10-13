from common import *
import json, time
t0=time.time()
HW=json.load(open(W+'/H_work.json'))
refw=cv2.imread(W+'/ref_work.jpg')
wh,ww=refw.shape[:2]          # 3212 x 1500
FW=8000; F=FW/ww; FH=int(round(wh*F))
print('canvas',FW,FH,flush=True)
acc=np.zeros((FH,FW,3),np.float32); ws=np.zeros((FH,FW),np.float32)
S=np.diag([F,F,1.0])
refg_blur=cv2.GaussianBlur(refw.astype(np.float32),(0,0),25)
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
# order: mid shots (scale>0.2) by coverage, then close-ups; ref last as filler
names=sorted(HW,key=lambda n:(HW[n]['scale']<0.2, -HW[n]['inl']))
names=[n for n in names if n!='IMG_4197.jpeg' or True]
def glare_mask(img):
    L=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[:,:,0].astype(np.float32)
    s=max(img.shape[:2])/1500
    small=cv2.resize(L,None,fx=1/s,fy=1/s,interpolation=cv2.INTER_AREA)
    bg=cv2.medianBlur(small.astype(np.uint8),51).astype(np.float32)
    g=np.clip((small-bg-8)/18,0,1)
    g=cv2.GaussianBlur(g,(0,0),6)
    return cv2.resize(g,(img.shape[1],img.shape[0]))
for n in names+['IMG_4203.jpeg']:
    t1=time.time()
    im=load(n)
    if n=='IMG_4203.jpeg':
        Hw=cv2.getPerspectiveTransform(QUAD,canvas_quad(0.25)); res_w=1e-3
    else:
        Hw=np.array(HW[n]['H']); sc=HW[n]['scale']*F  # canvas px per photo px
        res_w=(1.0/sc)**4
    Hf=S@Hw
    h,w=im.shape[:2]
    cr=cv2.perspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2),Hf).reshape(-1,2)
    x0=int(max(0,np.floor(cr[:,0].min())-4)); x1=int(min(FW,np.ceil(cr[:,0].max())+4))
    y0=int(max(0,np.floor(cr[:,1].min())-4)); y1=int(min(FH,np.ceil(cr[:,1].max())+4))
    rw_,rh_=x1-x0,y1-y0
    T=np.array([[1,0,-x0],[0,1,-y0],[0,0,1]],float)@Hf
    gm=glare_mask(im)
    img=cv2.warpPerspective(im,T,(rw_,rh_),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    mask=cv2.warpPerspective(np.ones((h,w),np.uint8)*255,T,(rw_,rh_),flags=cv2.INTER_NEAREST)
    gl=cv2.warpPerspective(gm,T,(rw_,rh_),flags=cv2.INTER_LINEAR)
    # low-frequency gain to match reference lighting (computed at work scale)
    if n!='IMG_4203.jpeg':
        pw=cv2.warpPerspective(im,Hw,(ww,wh),flags=cv2.INTER_AREA).astype(np.float32)
        pm=cv2.warpPerspective(np.ones((h,w),np.float32),Hw,(ww,wh))
        pm=cv2.erode(pm,np.ones((15,15)))
        num=cv2.GaussianBlur(refg_blur*pm[...,None],(0,0),25); den=cv2.GaussianBlur(cv2.GaussianBlur(pw,(0,0),25)*pm[...,None],(0,0),25)
        gain=np.clip(num/np.maximum(den,1),0.6,1.6)
        # extend gain outside overlap smoothly
        g_roi=cv2.resize(gain[int(y0/F):int(np.ceil(y1/F))+1,int(x0/F):int(np.ceil(x1/F))+1],None,fx=F,fy=F,interpolation=cv2.INTER_LINEAR)
        g_roi=g_roi[(y0-int(y0/F)*F).__int__() if False else 0:,:]
        oy=int(round(y0-int(y0/F)*F)); ox=int(round(x0-int(x0/F)*F))
        g_roi=g_roi[oy:oy+rh_,ox:ox+rw_]
        if g_roi.shape[0]<rh_ or g_roi.shape[1]<rw_:
            g_roi=cv2.resize(g_roi,(rw_,rh_))
        img*=g_roi
    # fine alignment against current mosaic (half res)
    cov=ws[y0:y1,x0:x1]>1e-9
    if n!='IMG_4203.jpeg' and cov[mask>0].mean()>0.15:
        mos=acc[y0:y1,x0:x1]/np.maximum(ws[y0:y1,x0:x1],1e-12)[...,None]
        tgt=np.where(cov[...,None],mos,img)
        a=cv2.resize(cv2.cvtColor(np.clip(tgt,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY),None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA)
        b=cv2.resize(cv2.cvtColor(np.clip(img,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY),None,fx=.5,fy=.5,interpolation=cv2.INTER_AREA)
        cl=cv2.createCLAHE(2.0,(16,16)); a=cl.apply(a); b=cl.apply(b)
        fl=dis.calc(a,b,None)
        fl[...,0]=cv2.GaussianBlur(fl[...,0],(0,0),12); fl[...,1]=cv2.GaussianBlur(fl[...,1],(0,0),12)
        mag=np.linalg.norm(fl,axis=2)
        print('  flow median',round(float(np.median(mag)),2),'p95',round(float(np.percentile(mag,95)),2),'(half-res px)',flush=True)
        fl=np.clip(fl,-40,40)
        fl=cv2.resize(fl,(rw_,rh_))*2
        gx,gy=np.meshgrid(np.arange(rw_,dtype=np.float32),np.arange(rh_,dtype=np.float32))
        mx=gx+fl[...,0]; my=gy+fl[...,1]
        img=cv2.remap(img,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        mask=cv2.remap(mask,mx,my,cv2.INTER_NEAREST,borderValue=0)
        gl=cv2.remap(gl,mx,my,cv2.INTER_LINEAR)
    mask=cv2.erode(mask,np.ones((9,9),np.uint8))
    dist=cv2.distanceTransform((mask>0).astype(np.uint8),cv2.DIST_L2,5)
    feather=np.clip(dist/180.0,0,1)
    wgt=(res_w*feather*(1-gl)**3).astype(np.float32)
    acc[y0:y1,x0:x1]+=img*wgt[...,None]; ws[y0:y1,x0:x1]+=wgt
    print(n,'roi',(x0,y0,x1,y1),'res_w',f'{res_w:.3g}',f'{time.time()-t1:.1f}s',flush=True)
out=np.clip(acc/np.maximum(ws,1e-12)[...,None],0,255).astype(np.uint8)
print('holes',int((ws<=1e-12).sum()),flush=True)
cv2.imwrite(W+'/replica_raw.png',out)
cv2.imwrite(W+'/replica_preview.jpg',cv2.resize(out,None,fx=0.125,fy=0.125,interpolation=cv2.INTER_AREA),[cv2.IMWRITE_JPEG_QUALITY,88])
print('DONE',f'{time.time()-t0:.0f}s',flush=True)
