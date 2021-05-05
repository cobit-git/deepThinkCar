import cv2
import datetime
from cobit_lane_follower import CobitLaneFollower



__SCREEN_WIDTH = 1280/4
__SCREEN_HEIGHT = 720/4
#__SCREEN_WIDTH = 320
#__SCREEN_HEIGHT = 240

SCREEN_WIDTH = 1280/4
SCREEN_HEIGHT =720/4
#SCREEN_WIDTH = 320
#SCREEN_HEIGHT = 240


lane_follower = CobitLaneFollower()
cap = cv2.VideoCapture(0)

cap.set(3, int(SCREEN_WIDTH))
cap.set(4, int(SCREEN_HEIGHT))

while True:
	ret, img_org = cap.read()
	
	if ret:
		lane_lines, img_lane = lane_follower.get_lane(img_org)
		angle, img_lane = lane_follower.get_steering_angle(img_lane, lane_lines)
		if img_lane is None:
			pass
		else:
			print(angle)
			
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else:
		print("cap error")

cap.release()
cv2.destroyAllWindows()
