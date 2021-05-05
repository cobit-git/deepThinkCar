import pygame
from pygame.locals import *
from adafruit_servokit import ServoKit
import RPi.GPIO as IO

pwmPin = 19
dirPin = 13

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(pwmPin, IO.OUT)
IO.setup(dirPin,IO.OUT)

p = IO.PWM(pwmPin, 100)
p.start(0)

class RemoteControl(object):

    def __init__(self):
        pygame.init()
        pygame.display.set_mode((320, 320))
        self.kit = ServoKit(channels=16)
        self.send_inst = True
        self.angle = 90
        self.kit.servo[0].angle = self.angle
        self.steer()

    def steer(self):
        while self.send_inst:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    key_input = pygame.key.get_pressed()

                    if key_input[pygame.K_UP]:
                        print("key up")
                    elif key_input[pygame.K_LEFT]:
                        self.angle = self.angle + 10
                        if self.angle > 160:
                            self.angle = 160
                        self.kit.servo[0].angle = self.angle
                        print("key left")
                    elif key_input[pygame.K_RIGHT]:
                        self.angle = self.angle - 10
                        if self.angle < 20:
                            self.angle = 20
                        self.kit.servo[0].angle = self.angle
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
                        self.send_inst = False
                        self.kit.servo[0].angle = 90
                        break

if __name__ == '__main__':
    RemoteControl()