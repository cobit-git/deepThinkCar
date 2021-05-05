import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

while True:
    kit.servo[0].angle = 150
    print("test1")
    time.sleep(1)
    kit.servo[0].angle = 90
    time.sleep(1)
    print("test2")
    kit.servo[0].angle = 30
    time.sleep(1)
    print("test3")
