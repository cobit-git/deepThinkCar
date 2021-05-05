import pygame
from pygame.locals import *
from adafruit_servokit import ServoKit
import RPi.GPIO as IO
import cv2
import datetime
import imutils
from threading import Thread, Event
import time 

pwmPin = 19
dirPin = 13

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(pwmPin, IO.OUT)
IO.setup(dirPin,IO.OUT)

__SCREEN_WIDTH = 320
__SCREEN_HEIGHT = 240

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

p = IO.PWM(pwmPin, 100)
p.start(0)


pygame.init()
pygame.display.set_mode((320, 320))

kit = ServoKit(channels=16)
send_inst = True
angle = 90
img_org =None
kit.servo[0].angle = angle

class CapThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, SCREEN_WIDTH)
        self.cap.set(4, SCREEN_HEIGHT)
        print("cap thread start")

    def run(self):
        global img_org
        while True:
            ret, img_org = self.cap.read()
            if (ret):
                cv2.imshow('my win', img_org)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

cap_thread = CapThread()
cap_thread.start()

img_idx = 0

while send_inst:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            key_input = pygame.key.get_pressed()

            if key_input[pygame.K_UP]:
                print("key up")
            elif key_input[pygame.K_LEFT]:
                angle = angle + 10
                if angle > 160:
                    angle = 160
                kit.servo[0].angle = angle
                if img_org.any():
                    cv2.imwrite("%s_%03d_%03d.png" % ("rc_img", img_idx, angle), img_org)
                    img_idx += 1
                print("key left")
            elif key_input[pygame.K_RIGHT]:
                angle = angle - 10
                if angle < 20:
                    angle = 20
                kit.servo[0].angle = angle
                if img_org.any():
                    cv2.imwrite("%s_%03d_%03d.png" % ("rc_img", img_idx, angle), img_org)
                    img_idx += 1
                print("key right")
            elif key_input[pygame.K_DOWN]:
                print("key down")
            elif key_input[pygame.K_s]:
                print("motor start")
                p.ChangeDutyCycle(40)
            elif key_input[pygame.K_t]:
                print("motor stop")
                p.ChangeDutyCycle(0)
            elif key_input[pygame.K_q]:
                print("exit")
                send_inst = False
                kit.servo[0].angle = 90
                break

