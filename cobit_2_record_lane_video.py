import cv2
from adafruit_servokit import ServoKit
from cobit_opencv_lane_detect import CobitOpencvLaneDetect
from cobit_car_motor_l9110 import CobitCarMotorL9110

def main_loop():
	"""
	2단계: OpenCV를 이용한 차선인식 및 비디오 래코딩 주행 \n
	OpenCV를 이용해서 차선의 각도를 인식하고, 차량 스티어링 휠을 회전함 \n
	차량 구동용 DC모터를 동작시켜서 차량을 전진시킴. 차선은 빨간색으로 고정되어 있음  \n
	차량이 차선을 정확하게 따라 가면서 촬영된 주행 영상을 저장함  
	"""
	servo = ServoKit(channels=16)
	cv_detector = CobitOpencvLaneDetect()
	motor = CobitCarMotorL9110()

	SCREEN_WIDTH = 320
	SCREEN_HEIGHT = 240

	cap = cv2.VideoCapture(0)
	cap.set(3, SCREEN_WIDTH)
	cap.set(4, SCREEN_HEIGHT)

	# Below code works normally for Pi camera V2.1
	# But for ELP webcam, it doesn't work.
	#fourcc =  cv2.VideoWriter_fourcc(*'XVID')
	fourcc =  cv2.VideoWriter_fourcc('M','J','P','G')

	video_orig = cv2.VideoWriter('./data/car_video.avi', fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))
	#video_lane = cv2.VideoWriter('./data/car_video_lane.avi', fourcc, 20.0, (SCREEN_WIDTH, SCREEN_HEIGHT))
		
	servo_offset = 15
	servo.servo[0].angle = 90 + servo_offset

	for i in range(30):
		ret, img_flip = cap.read()
		img_flip_v = cv2.flip(img_flip, 0)
		img_org = cv2.flip(img_flip_v, 1)
		if ret:
			lanes, img_lane = cv_detector.get_lane(img_org)
			angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
			if img_angle is None:
				print("angle image out!!")
				pass
			else:
				print(angle)
				servo.servo[0].angle = angle + servo_offset			
				cv2.imshow("img_angle", img_angle)
				cv2.waitKey(1)
		else:
			print("cap error")
		
	motor.motor_move_forward(30)

	while True:
		ret, img_flip = cap.read()
		img_flip_v = cv2.flip(img_flip, 0)
		img_org = cv2.flip(img_flip_v, 1)
		if ret:
			cv2.imshow('lane', img_org)
			video_orig.write(img_org)
			lanes, img_lane = cv_detector.get_lane(img_org)
			
			angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
			if img_angle is None:
				pass
			else:
				#video_lane.write(img_lane)
				
				print(angle)
				servo.servo[0].angle = angle + servo_offset
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		else:
			print("cap error")
			
	motor.motor_stop()
	cap.release()
	video_orig.release()
	#video_lane.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main_loop()
