import RPi.GPIO as IO
import time

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(8, IO.OUT)
#IO.setup(25,IO.OUT)


while 1:
        
        IO.output(8, True)
        time.sleep(1)
        IO.output(8, False)
        time.sleep(1)

