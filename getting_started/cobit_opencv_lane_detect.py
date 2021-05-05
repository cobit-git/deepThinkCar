import cv2
import numpy as np
import logging
import math
import datetime
import sys

_SHOW_IMAGE = False
class CobitOpencvLaneDetect(object):
    """
    OpenCV 기반 차선 검츨 클래스 \n
    이 클래스는 차량의 카메라와 OpenCV의 color기반 오브젝트 디텍션을 이용해서
    차량의 앞 차선의 각도를 검출함. 

    :Example:
        cv_detector = CobitOpencvLaneDetect() \n
        lanes, img_lane = cv_detector.get_lane(img_org) \n 
        angle, img_angle = cv_detector.get_steering_angle(img_lane, lanes)
    """
    def __init__(self):
        self.curr_steering_angle = 90

    def get_lane(self, frame):
        """
        입력된 이미지 파일에서 차선을 발견하고, 차선의 좌표값을 어레이로 얻음.

        :param frame: 카메라에서 전달된 차량 앞, 차선의 이미지 파일 
        :return lane_lines: 차선의 좌표값 np 어레이 데이터    
        :return final_frame: 카메라에서 전달된 차량 앞 이미지  
        """   
        _show_image("orignal", frame)
        lane_lines, frame = _detect_lane(frame)
        return lane_lines, frame

    def get_steering_angle(self, img_lane, lane_lines):
        """
        입력된 이미지 파일과 차선의 좌표값 np 어레이에서 차량의 스티어링 휠 회전 각도를 얻음.

        :param img_lane: 카메라에서 전달된 차량 앞, 차선의 이미지 파일  
        :param lane_lines: 차선의 좌표값 np 어레이 데이터 
        :return curr_heading_image: 차선을 녹색/적색 직선으로 표시한 차량 앞 이미지
        :return curr_heading_angle: 차선의 각도, 즉 차량의 스티어링 휠이 회전할 각도 
        """   
        if len(lane_lines) == 0:
            return 0, None
        new_steering_angle = _compute_steering_angle(img_lane, lane_lines)
        self.curr_steering_angle = _stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))

        curr_heading_image = _display_heading_line(img_lane, self.curr_steering_angle)
        _show_image("heading", curr_heading_image)

        return self.curr_steering_angle, curr_heading_image

############################
# Frame processing steps
############################
def _detect_lane(frame):
    logging.debug('detecting lane lines...')
    edges = _detect_edges(frame)
    #_show_image('edges', edges)

    cropped_edges = _region_of_interest(edges)
    #_show_image('edges cropped', cropped_edges)

    line_segments = _detect_line_segments(cropped_edges)
    line_segment_image = _display_lines(frame, line_segments)
    #_show_image("line segments", line_segment_image)

    lane_lines = _average_slope_intercept(frame, line_segments)
    lane_lines_image = _display_lines(frame, lane_lines)
    #_show_image("lane lines images", lane_lines_image)
    #lane_lines_resized = cv2.resize(lane_lines_image, dsize=(320, 180), interpolation=cv2.INTER_AREA)
    #__show_image("lane lines", lane_lines_resized)

    return lane_lines, lane_lines_image


def _get_mask(frame):
     # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #_show_image("hsv", hsv)
    # blue 
    #lower_blue = np.array([80, 150, 0])
    #upper_blue = np.array([110, 255, 255])
    # red 
    lower_blue1 = np.array([0, 100, 100])
    upper_blue1 = np.array([20, 255, 255])
    #lower_blue = np.array([130, 100, 20])
    #upper_blue = np.array([180, 255, 255])
    #black 
    #lower_blue = np.array([0, 5, 50])
    #upper_blue = np.array([179, 200, 255])
    mask1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
    lower_blue2 = np.array([160, 100, 100])
    upper_blue2 = np.array([180, 255, 255])

    mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask = mask1+mask2

    return mask

def _detect_edges(mask):
    # filter for blue lane lines
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #_show_image("hsv", hsv)
    # blue 
    #lower_blue = np.array([80, 150, 0])
    #upper_blue = np.array([110, 255, 255])
    # red 
    #lower_blue1 = np.array([0, 100, 100])
    #upper_blue1 = np.array([20, 255, 255])
    #lower_blue = np.array([130, 100, 20])
    #upper_blue = np.array([180, 255, 255])
    #black 
    #lower_blue = np.array([0, 5, 50])
    #upper_blue = np.array([179, 200, 255])
    #mask1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
    #lower_blue2 = np.array([160, 100, 100])
    #upper_blue2 = np.array([180, 255, 255])

    #mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    #mask = mask1+mask2

    #_show_image("blue mask", mask, True)

    # detect edges
    #edges = cv2.Canny(mask, 200, 400)
    edges = cv2.Canny(mask, 200, 400)
    #_show_image("blue edge", edges)

    return edges

def _region_of_interest(canny):
    height, width = canny.shape
    mask = np.zeros_like(canny)

    # only focus bottom half of the screen
    
    polygon = np.array([[
        (0, height*(1/2)),
        (width, height*(1/2)),
        (width, height),
        (0, height),
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

def _detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=15, maxLineGap=4)

    if line_segments is not None:
        for line_segment in line_segments:
            logging.debug('detected line_segment:')
            logging.debug("%s of length %s" % (line_segment, _length_of_line_segment(line_segment[0])))

    return line_segments


def _average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen
    
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    #left_fit.append((slope, intercept))
                    if slope < -0.75:
                        #print("left points:", x1, x2, y1, y2) 
                        #print("left slope", slope, "intercepts:", intercept)
                        left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    #right_fit.append((slope, intercept))
                    if slope > 0.75:
                        #print("right points:", x1, x2, y1, y2) 
                        #print("right slope", slope, "intercepts:", intercept)
                        right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(_make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(_make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines
 

def _compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle


def _stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """
    if num_of_lane_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane
    
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
                                        + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))
    return stabilized_steering_angle


"""
  Utility Functions
"""
def _display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image


def _display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
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


def _length_of_line_segment(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def _show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)


def _make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]


