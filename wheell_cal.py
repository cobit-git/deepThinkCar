from adafruit_servokit import ServoKit
import RPi.GPIO as IO
import time

offset = 0

servo = ServoKit(channels=16)
angle = 90
servo.servo[0].angle = angle+offset

pwmPin = 19
dirPin = 13

pwmPin2 = 12
dirPin2 = 16

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(pwmPin, IO.OUT)
IO.setup(dirPin,IO.OUT)
IO.setup(pwmPin2, IO.OUT)
IO.setup(dirPin2,IO.OUT)
p2 = IO.PWM(pwmPin2, 100)
p2.start(0)



p = IO.PWM(pwmPin, 100)
p.start(0)

p.ChangeDutyCycle(40)
p2.ChangeDutyCycle(40)
time.sleep(3)



