#-*- coding:utf-8 -*-
import cv2 
import sys
import glob
import serial
import threading
#from threading import Thread 
import time
from cobit_serial_vehicle_manager import SerialVehicleManager
#from cobit_opencv_cam_rc import CobitOpenCVCamRC

# 운행중 이미지를 저장하려면 아래 변수를 True로 변경할 것 
LANE_RECORDING = False

def main_loop():
    """
    1단계: 리모컨 조종을 통한 차선 주행 \n
    사용자가 리모컨을 통해서 차량이 차선을 따라가도록 조종함  \n
    조종에 익숙해 지기전에는 LANE_RECORDING을 False로 할 것   \n
    조종에 익숙해 지면 LANE+RECORDING을 True로 하고 트랙을 10~20회 주행하면 딥러닝 학습에 충분한 데이터를 확보 할 수 있음  
    """
    vehicle = SerialVehicleManager("/dev/ttyUSB0")

    SCREEN_WIDTH = 320
    SCREEN_HEIGHT = 240

    cap = cv2.VideoCapture(0)
    cap.set(3, int(SCREEN_WIDTH))
    cap.set(4, int(SCREEN_HEIGHT))

    vehicle.start()
    vehicle.open_port()

    #t = threading.Thread(target=vehicle.update, args=())
    #t.daemon = True
    #t.start

    i = 0
    video_file = "data/cobit"
    angle = 30

    while True:
        
        ret, img_flip = cap.read()
        img_org = cv2.flip(img_flip, 0)
        if LANE_RECORDING is True:
            cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, angle), img_org)
            i += 1
        if ret:
            cv2.imshow('win', img_org)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("cap error")
    cap.release()
    vehicle.finish()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main_loop()

   





   







