import cv2
import numpy as np
import logging
import math
import tensorflow as tf
from keras.models import load_model

_SHOW_IMAGE = False

class CobitDeepLaneDetect(object):

    """
    딥러닝 기반 차선 검츨 클래스 \n
    이 클래스는 차량의 카메라와 OpenCV의 color기반 오브젝트 디텍션을 이용해서
    차량의 앞 차선의 각도를 검출함

    Example::
        deep_detector = CobitDeepLaneDetect('home/pi/user/model') \n
        deep_detector.follow_line()

    :param model_path: 딥러닝 트레이닝 된 추론 파일(.h5)의 디렉토리 경로  
    """
    def __init__(self, model_path):
        logging.info('Creating a EndToEndLaneFollower...')

        self.curr_steering_angle = 90
        
        if model_path is None:
            print("wrong model path!")
            return 
        else:
            self.model = load_model(model_path)
    
    def follow_lane(self, frame):
        """
        입력된 이미지 파일에서 차선을 발견하고, 발견된 차선의 각도에 따라 스티어링 
        휠의 회전 각도를 결정함 

        :param frame: 카메라에서 전달된 차량 앞, 차선의 이미지 파일  
        :return curr_streering_angle: 차량의 스티어링 휠의 회전 각도 
        :return final_frame: 카메라에서 전달된 차량 앞 이미지
        """    
        _show_image("orig", frame)
        self.curr_steering_angle = self.__compute_steering_angle(frame)
        logging.debug("curr_steering_angle = %d" % self.curr_steering_angle)
        final_frame = _display_heading_line(frame, self.curr_steering_angle)

        return self.curr_steering_angle, final_frame 

    def __compute_steering_angle(self, frame):
        """
        입력된 이미지 파일에서 차선을 발견하고, 발견된 차선의 각도에 따라 스티어링 
        휠의 회전 각도를 결정함 \n
        follow_lane() 함수 내에서 사용됨 
        """
        preprocessed = _img_preprocess(frame)
        X = np.asarray([preprocessed])
        #steering_angle = self.model.predict(X)[0]
        steering_angle = self.model(X, training=False)[0]

        logging.debug('new steering angle: %s' % steering_angle)
        return int(steering_angle + 0.5) # round the nearest integer

def _img_preprocess(image):
    """
    다음 세가지를 수행함.
    - 입력된 이미지의 아래 절반만 사용하도록 사이즈를 조정하고.
    - BGR 컬러를 YUV 컬러로 변경.
    - nVidia 딥러닝 모델에서 사용하도록 이미지 사이즈를 200x66으로 조종.
    compute_steering_angle() 함수 내에서 사용됨. 
    """
    height, _, _ = image.shape
    image = image[int(height/2):,:,:]  # remove top half of the image, as it is not relevant for lane following
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)  # Nvidia model said it is best to use YUV color space
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
    image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
    return image

def _display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    """
    차량 앞 이미지와 차선 각도를 입력받아 이미지에 차선 각도를 표시하는 녹색/적색 직선을 그림.
    각도 표시 직선이 그려진 차량 앞 이미지를 돌려줌 
    """
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

def _show_image(title, frame, show=_SHOW_IMAGE):
    """
    show 변수의 부울값에 따라 frame 이미지를 OpenCV 이용하여 디스플레이 함 
    Example:: 
        show = True # 이미지를 디스플레이 함 
        show = False # 이미지를 디스플레이 하지 않음 
    """
    if show:
        cv2.imshow(title, frame)
