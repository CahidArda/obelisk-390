import cv2,numpy as np
from PIL import Image,ImageOps
rep=cv2.imread('/workspace/home/work/replica.png')
X0,Y0,X1,Y1=3150,350,5150,1800
im=np.array(ImageOps.exif_transpose(Image.open('/workspace/home/uploads2/IMG_4234.jpeg')).convert('RGB'))[:,:,::-1].copy()
H=np.load('/workspace/home/work/Hg_IMG_4234.npy')
T=np.array([[1,0,-X0],[0,1,-Y0],[0,0,1]],float)
w=cv2.warpPerspective(im,T@H,(X1-X0,Y1-Y0),flags=cv2.INTER_CUBIC).astype(np.float32)
valid=cv2.warpPerspective(np.ones(im.shape[:2],np.uint8),T@H,(X1-X0,Y1-Y0))
R=rep[Y0:Y1,X0:X1].astype(np.float32)
# flat-field the photo to the replica's local paper tone
k=61
bgw=np.stack([cv2.GaussianBlur(cv2.medianBlur(np.clip(w[...,c],0,255).astype(np.uint8),k).astype(np.float32),(0,0),25) for c in range(3)],-1)
bgr=np.stack([cv2.GaussianBlur(cv2.medianBlur(R[...,c].astype(np.uint8),k).astype(np.float32),(0,0),25) for c in range(3)],-1)
wf=np.clip(w/np.maximum(bgw,10)*bgr,0,255)
# blend mask: rounded box around the composition, feathered
m=np.zeros(R.shape[:2],np.float32)
cv2.rectangle(m,(3330-X0,560-Y0),(4950-X0,1640-Y0),1,-1)
m=cv2.GaussianBlur(m,(0,0),60)*(cv2.erode(valid,np.ones((41,41),np.uint8))>0)
out=R*(1-m[...,None])+wf*m[...,None]
rep[Y0:Y1,X0:X1]=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('/workspace/home/work/replica.png',rep)
np.save('/workspace/home/work/r.npy',rep)
cv2.imwrite('/workspace/home/work/goldpatch.jpg',cv2.resize(rep[Y0:Y1,X0:X1],None,fx=.5,fy=.5),[cv2.IMWRITE_JPEG_QUALITY,90])
print('ok')
