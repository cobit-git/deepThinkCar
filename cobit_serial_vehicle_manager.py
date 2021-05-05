#-*- coding:utf-8 -*-
import serial 
from threading import Thread
from adafruit_servokit import ServoKit
from cobit_car_motor_l9110 import CobitCarMotorL9110


class SerialVehicleManager(Thread):
    
    """
    딥트카 리모컨 구동 클래스 \n
    딥트카의 리모컨을 구동하기 위해서는 리모컨 수신기 모듈을 딥트카 라즈베리파이 USB에 장착함  \n
    그 다음에 이 클래스를 활용하여 리모컨을 동작시킴 (cobit_1_lane_follower_rc 참조)  \n
    이 클래스는 리모컨 수신을 쓰래드를 통해서 실행함 

    Example::
        vehicle = SerialVehicleManager("/dev/ttyUSB0")
       
    """
    def __init__(self, serial_port):

        Thread.__init__(self)
        self.seq = serial.Serial(
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.motor = CobitCarMotorL9110()
        self.servo = ServoKit(channels=16)
        self.servo_offset = 0
        self.seq.port = serial_port
        self.is_serial_running = False
        self.daemon = True
        self.command = None

       
    def read_cmd(self):
        """
        리모컨 수신기에서 전달된 명령을 읽어오기 
        """
        return self.command

       
    def run(self):
        """
        (쓰래드) 수신기에서 전달되는 명령을 실시간으로 가져옴 
        """
        while True: 
            if self.seq.isOpen() == True:  
                try:
                    if self.seq.inWaiting():
                        try:
                            self.command = self.seq.readline()
                            angle = self.get_angle()
                            if angle is not -1:
                                #print(angle)
                                self.servo.servo[0].angle = angle + self.servo_offset

                            throttle = self.get_throttle()
                            if throttle is not -1:
                                #if throttle > 55:
                                throttle -= 50
                                throttle *= 2
                                print(throttle)
                                if throttle > 10:
                                    self.motor.motor_move_forward(throttle)
                                else:
                                    self.motor.motor_move_forward(0)
                                #elif throttle < 45:
                                #    throttle = 100- throttle*2
                                #    print(throttle)
                                #    motor.motor_move_backward(throttle)
                                #elif throttle > 40 and throttle < 60:
                                #    motor.motor_stop()
                                
                                    

                        except AttributeError:
                            print("attr error")
                except IOError:
                    print("IO error")

    def open_port(self):
        """
        리모컨 수신기를 위한 시리얼 포트를 오픈함 
        """
        if self.seq.isOpen() == False:
            self.seq.open()

    def close_port(self):
        """
        리모컨 수신기를 위한 시리얼 포트를 클로즈함 
        """
        if self.seq.isOpen() == True:
            self.seq.close()

    def is_seq_open(self):
        """
        리모컨 수신기를 위한 시리얼 포트가 오픈 되어 있는지 점검  
        """
        if self.seq.isOpen() == True:
            return True
        else:
            return False

    #def set_serial_port(self, port_name):
    #    self.seq.port = port_name

    def get_serial_port(self):
        """
        리모컨 수신기를 위한 시리얼 포트 번호를 가져옴
        """
        return self.seq.port

    def get_angle(self):
        """
        리모컨 수신기에서 전달된 패킷에서 스티어링 각도 값을 읽음 
        """
        cmd = str(self.command)
        start = cmd.find('x')
        end = cmd.find('y')
        if start is not -1 and end is not -1:
            joy_num = int(cmd[start+1:end])
            angle = joy_num/10 + 40 
            return angle
        else:
            return -1

    def get_throttle(self):
        """
        리모컨 수신기에서 전달된 패킷에서 스티어링 쓰로틀 값을 읽음 
        """
        cmd = str(self.command)
        start = cmd.find('y')
        end = cmd.find('z')
        if start is not -1 and end is not -1:
            throttle_num = int(cmd[start+1:end])
            throttle = throttle_num/10
            return throttle
        else:
            return -1

    def finish(self):
        """
        차량의 스티ㅓ일 휠 각도와 쓰로틀 값을 초기화 함 
        """
        self.servo.servo[0].angle = 90+self.servo_offset
        self.motor.motor_stop()


        

if __name__ =='__main__':
    vehicle = SerialVehicleManager("/dev/ttyUSB0")
    vehicle.open_port()
    vehicle.run()
