import cv2,numpy as np,sys,json
from PIL import Image,ImageOps
rep=np.load('/workspace/home/work/r.npy',mmap_mode='r')
X0,Y0,X1,Y1=3300,450,5000,1650
R=np.ascontiguousarray(rep[Y0:Y1,X0:X1])
b=cv2.cvtColor(R,cv2.COLOR_BGR2LAB)[...,2].astype(np.float32)
rb=np.clip(b-cv2.GaussianBlur(b,(0,0),20),0,None); rb=cv2.GaussianBlur(rb,(0,0),1.5); rb/=np.percentile(rb,99.5)
im=np.array(ImageOps.exif_transpose(Image.open('/workspace/home/uploads2/IMG_4234.jpeg')).convert('RGB'))[:,:,::-1].copy()
H=np.load(sys.argv[1]) if len(sys.argv)>1 else cv2.getPerspectiveTransform(np.float32([[856,1269],[2086,1753],[2055,1566],[1682,2094]]),np.float32([[3810,737],[4805,1321],[4741,1235],[4517,1480]]))
T=np.array([[1,0,-X0],[0,1,-Y0],[0,0,1]],float)
w=cv2.warpPerspective(im,T@H,(X1-X0,Y1-Y0))
L=cv2.cvtColor(w,cv2.COLOR_BGR2GRAY).astype(np.float32); e=np.clip(128+(L-cv2.GaussianBlur(L,(0,0),25))*5,0,255).astype(np.uint8)
rb_=np.clip(255-rb*230,0,255).astype(np.uint8)
for name,img in [('gridR',rb_),('gridP',e)]:
    c=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    for x in range(0,X1-X0,100):
        cv2.line(c,(x,0),(x,c.shape[0]),(0,0,255) if (x+X0)%500==0 else (230,160,160),1)
        cv2.putText(c,str(x+X0),(x+3,22),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,200),1)
    for y in range(0,Y1-Y0,100):
        cv2.line(c,(0,y),(c.shape[1],y),(0,0,255) if (y+Y0)%500==0 else (230,160,160),1)
        cv2.putText(c,str(y+Y0),(3,y-4),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,200),1)
    cv2.imwrite(f'/workspace/home/work/{name}.jpg',cv2.resize(c,None,fx=0.6,fy=0.6,interpolation=cv2.INTER_AREA))
np.save('/workspace/home/work/Hcur.npy',H)
print('ok')
