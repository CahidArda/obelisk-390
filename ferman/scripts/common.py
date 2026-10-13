import cv2, numpy as np, os, json
from PIL import Image, ImageOps
UP='/workspace/home/uploads'; W='/workspace/home/work'
ASPECT=0.467
CW=6000; CH=int(round(CW/ASPECT))  # final canvas
QUAD=np.float32([[1182,1222],[2805,1137],[2907,4684],[1251,4690]])  # TL TR BR BL in IMG_4203
def load(name):
    im=ImageOps.exif_transpose(Image.open(os.path.join(UP,name))).convert('RGB')
    return np.array(im)[:,:,::-1].copy()
def canvas_quad(scale):
    w=CW*scale; h=CH*scale
    return np.float32([[0,0],[w,0],[w,h],[0,h]])
def gray(im):
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    return cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8)).apply(g)
