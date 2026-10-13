from common import *
im=cv2.imread(W+'/replica_raw.png').astype(np.float32)
H,Wd=im.shape[:2]
k=16
sm=cv2.resize(im,(Wd//k,H//k),interpolation=cv2.INTER_AREA)
# ink/gold mask at small scale: pixels much darker or more saturated than local paper
hsv=cv2.cvtColor(sm.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32)
bg=np.zeros_like(sm)
for c in range(3):
    bg[...,c]=cv2.medianBlur(sm[...,c].astype(np.uint8),41).astype(np.float32)
lum=sm.mean(2); blum=bg.mean(2)
ink=(lum<blum-12)|(hsv[...,1]>hsv[...,1].mean()+40)
# recompute background with ink replaced by local bg
sm2=sm.copy(); sm2[ink]=bg[ink]
for c in range(3):
    b=cv2.medianBlur(sm2[...,c].astype(np.uint8),31).astype(np.float32)
    bg[...,c]=cv2.GaussianBlur(b,(0,0),6)
paper=np.median(bg.reshape(-1,3),axis=0)
print('paper BGR',paper)
bgf=cv2.resize(bg,(Wd,H),interpolation=cv2.INTER_CUBIC)
out=im/np.maximum(bgf,20)*paper
# keep a little of the original large-scale variation (5%) so it doesn't look synthetic
out=0.95*out+0.05*im
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite(W+'/replica.png',out)
cv2.imwrite(W+'/replica_preview2.jpg',cv2.resize(out,None,fx=0.06,fy=0.06,interpolation=cv2.INTER_AREA),[cv2.IMWRITE_JPEG_QUALITY,88])
print('ok')
