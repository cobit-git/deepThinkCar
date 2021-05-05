import RPi.GPIO as IO
import time



class CobitCarMotorL9110():

    """
    딥트카 구동용 DC모터 구동 클래스 \n
    딥트카 구동을 위해서 2개의 DC 기어드 모터를 사용함 \n
    모터의 라즈베리파이 GPIO 연결은 다음과 같음

    모터 1  \n
        PWM pin = 19 (GPIO no 35)       IA1  \n
        Direction pin = 13 (GPIO no 33) IB1  \n

    모터 2 
        PWM pin = 12 (GPIO no 32)       IA2  \n
        Dirction pin = 16 (GPIO no 36)  IB2  \n

    Example::
        motor = CobitCarMotorL9110()   \n
        motor.motor_move_forward(60)   \n
        motor.motor_stop()             \n
    """
    def __init__(self):
        self.motor1_r_pwmPin = 19
        self.motor1_r_dirPin = 13
        self.motor2_l_pwmPin = 12
        self.motor2_l_dirPin = 16
        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(self.motor1_r_pwmPin, IO.OUT)
        IO.setup(self.motor1_r_dirPin, IO.OUT)
        IO.setup(self.motor2_l_pwmPin, IO.OUT)
        IO.setup(self.motor2_l_dirPin, IO.OUT)
        self.motor1_pwm = IO.PWM(self.motor1_r_pwmPin, 100)
        self.motor1_pwm.start(0)
        self.motor2_pwm = IO.PWM(self.motor2_l_pwmPin, 100)
        self.motor2_pwm.start(0)


    def motor_move_forward(self, speed):
        """
        딥트카가 앞으로 전진시킴. 속도(speed)를 0 ~ 100까지 입력가능 \n
        0이면 딥트카가 멈추고 100이면 최고속도로 전진함  

        :param speed: a모터의 속도 0 ~ 100  
        """   
        if speed > 100:
            speed = 100
        self.motor1_pwm.ChangeDutyCycle(int(speed))
        self.motor2_pwm.ChangeDutyCycle(int(speed))
        
    def motor_stop(self):
        """
        딥트카를 멈춤. 모터를 정지함  
        """   
        self.motor1_pwm.ChangeDutyCycle(0)
        self.motor2_pwm.ChangeDutyCycle(0)

if __name__ == '__main__':

    cobit_motor = CobitCarMotorL9110()
    while True:
        cobit_motor.motor_move_forward(30)
        time.sleep(2)
        cobit_motor.motor_stop()
        time.sleep(2)
      

