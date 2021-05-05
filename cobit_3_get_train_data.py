import cv2
import sys
from cobit_opencv_lane_detect import CobitOpencvLaneDetect
import os 


def main_loop():
	"""
	3단계: 촬영된 주행 영상으로부터 딥러닝 학습용 데이터 얻기 \n
	촬영된 주행 영상에서 스틸 이미지르 하나씩 검출하고, 각 이미지의 차량 스티어링 휠 각도를 측정함 \n
	스티어링 휠 각도를 '라벨' 스틸 이미지를 데이터로 묶어서 저장함  
	"""
	video_file = "./data/car_video.avi"
	cv_detector = CobitOpencvLaneDetect()
	cap = cv2.VideoCapture(video_file)

	index = 0

	os.system("rm ./data/*.png")

	while True:
		ret, img_org = cap.read()
		if ret:
			lanes, img_lane = cv_detector.get_lane(img_org)
			cv2.imshow("ddd", img_org)
			angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
			if img_angle is None:
				pass
			else:
				cv2.imwrite("%s_%03d_%03d.png" % (video_file, index, angle), img_org)
				index += 1	
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		else:
			print("cap error")
			break

	cap.release()
	cv2.destroyAllWindows()

if __name__ =='__main__':
	main_loop()


