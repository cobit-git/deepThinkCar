import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print("Start servo motor test...")
for i in range(2):
    print("Servo angle 150 degree")
    kit.servo[0].angle = 150
    time.sleep(1)
    print("Servo angle 90 degree")
    kit.servo[0].angle = 90
    time.sleep(1)
    print("Servo angle 30 degree")
    kit.servo[0].angle = 30
    time.sleep(1)
print("Servo motor test completed")
kit.servo[0].angle = 90
time.sleep(1)
