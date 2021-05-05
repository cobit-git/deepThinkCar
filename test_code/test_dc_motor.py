import RPi.GPIO as GPIO # import GPIO librery

>>>from time import sleep

>>> GPIO.setmode(GPIO.BCM)

>>>Motor1A = 02 # set GPIO-02 as Input 1 of the controller IC

>>>Motor1B = 03 # set GPIO-03 as Input 2 of the controller IC

>>>Motor1E = 04 # set GPIO-04 as Enable pin 1 of the controller IC

>>>GPIO.setup(Motor1A,GPIO.OUT)

>>>GPIO.setup(Motor1B,GPIO.OUT)

>>>GPIO.setup(Motor1E,GPIO.OUT)

>>>pwm=GPIO.PWM(04,100) # configuring Enable pin means GPIO-04 for PWM

>>>pwm.start(50) # starting it with 50% dutycycle

>>>print "GO forward"

>>>GPIO.output(Motor1A,GPIO.HIGH)

>>>GPIO.output(Motor1B,GPIO.LOW)

>>>GPIO.output(Motor1E,GPIO.HIGH)

>>>sleep(2)

# this will run your motor in forward direction for 2 seconds with 50% speed.

>>>pwm.ChangeDutyCycle(80) # increasing dutycycle to 80

>>>print "GO backward"

>>>GPIO.output(Motor1A,GPIO.HIGH)

>>>GPIO.output(Motor1B,GPIO.LOW)

>>>GPIO.output(Motor1E,GPIO.HIGH)

>>>sleep(2)

# this will run your motor in reverse direction for 2 seconds with 80% speed by supplying 80% of the battery voltage

>>>print "Now stop"

>>>GPIO.output(Motor1E,GPIO.LOW)

>>>pwm.stop() # stop PWM from GPIO output it is necessary

>>>GPIO.cleanup()
