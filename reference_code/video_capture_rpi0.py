import cv2 as cv
import numpy as np
from urllib.request import urlopen
import os
import datetime
import time
import sys

#change to your ESP32-CAM ip
url="http://192.168.0.10:8000/stream.mjpg"
CAMERA_BUFFRER_SIZE=2048*8 #4096
stream=urlopen(url)
bts=b''
while True:
    bts+=stream.read(CAMERA_BUFFRER_SIZE)
    jpghead=bts.find(b'\xff\xd8')
    jpgend=bts.find(b'\xff\xd9')
    if jpghead>-1 and jpgend>-1:
        print("success")
        jpg=bts[jpghead:jpgend+2]
        bts=bts[jpgend+2:]
        buf = np.frombuffer(jpg,dtype=np.uint8)
        if buf.any():
            img=cv.imdecode(buf,cv.IMREAD_UNCHANGED)
            v=cv.flip(img,0)
            h=cv.flip(img,1)
            p=cv.flip(img,-1)        
            frame=p
            h,w=frame.shape[:2]
            #qimg=cv.resize(frame,(800,600))
            cv.imshow("a",img)
    else:
        print("fail")
    k=cv.waitKey(1)
    if k & 0xFF==ord('q'):
        break
cv.destroyAllWindows()