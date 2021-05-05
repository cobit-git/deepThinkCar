import cv2
from adafruit_servokit import ServoKit
from cobit_deep_lane_detect import CobitDeepLaneDetect
from cobit_car_motor_l9110 import CobitCarMotorL9110
import time

def main_loop():
    """
    5단계: 딥러닝 추론 파일에 의한 자율 주행  \n
    텐서플로에 의한 데이터 학습이 끝나고 출력된 추론파일(.h5)를 이용해서 자율주행을 실행 
    """
    deep_detector = CobitDeepLaneDetect("./models/lane_navigation_final.h5")
    motor = CobitCarMotorL9110()
    servo = ServoKit(channels=16)

    SCREEN_WIDTH = 320
    SCREEN_HEIGHT = 240

    cap = cv2.VideoCapture(0)
    cap.set(3, SCREEN_WIDTH)
    cap.set(4, SCREEN_HEIGHT)

    servo_offset = 20
    servo.servo[0].angle = 90 + servo_offset

    time.sleep(2)

    for i in range(30):
        ret, img_flip = cap.read()
        img_org = cv2.flip(img_flip, 0)
        if ret:
            angle_deep, img_angle = deep_detector.follow_lane(img_org)
            if img_angle is None:
                print("angle image out!!")
                pass
            else:
                print(angle_deep)
                servo.servo[0].angle = angle_deep + servo_offset			
                cv2.imshow("img_angle", img_angle)
                cv2.waitKey(1)
        else:
            print("cap error")

    motor.motor_move_forward(20)

    try:
        while cap.isOpened():
            ret, img_flip = cap.read()
            img_org = cv2.flip(img_flip, 0)
            angle_deep, img_angle = deep_detector.follow_lane(img_org)
            if img_angle is None:
                print("angle image out!!")
                pass
            else:
                print(angle_deep)
                servo.servo[0].angle = angle_deep + servo_offset

                cv2.imshow("img_angle", img_angle)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally: 
            cap.release()
            cv2.destroyAllWindows()

if __name__ =='__main__':
	main_loop()


        
