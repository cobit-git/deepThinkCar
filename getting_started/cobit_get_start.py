from PyQt5 import QtGui
from PyQt5.QtWidgets import * # QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
import time 
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from cobit_car_motor_l9110 import CobitCarMotorL9110
import cobit_opencv_lane_detect
from adafruit_servokit import ServoKit


class VideoThread(QThread):
    
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.curr_steering_angle = 90
        self.flag = False

    #def set_flag_false(self):
    #    self.flag = False

    #def set_flag_true(self):
    #    self.flag = True
        
    def run(self):
        # capture from web cam
        self.cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                if a.get_cv_mode() == 0:  # normal video display
                    self.change_pixmap_signal.emit(cv_img)

                elif a.get_cv_mode() == 1:  # Red color masking 
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_mask = cv2.cvtColor(cv_mask_, cv2.COLOR_GRAY2BGR)
                    self.change_pixmap_signal.emit(cv_mask)

                elif a.get_cv_mode() == 2: # Canny edge detect 
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_edge_ = cobit_opencv_lane_detect._detect_edges(cv_mask_)
                    cv_edge = cv2.cvtColor(cv_edge_, cv2.COLOR_GRAY2BGR)
                    self.change_pixmap_signal.emit(cv_edge)

                elif a.get_cv_mode() == 3:  # Crop image
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_edge_ = cobit_opencv_lane_detect._detect_edges(cv_mask_)
                    cv_crop_ = cobit_opencv_lane_detect._region_of_interest(cv_edge_) 
                    cv_crop = cv2.cvtColor(cv_crop_, cv2.COLOR_GRAY2BGR)
                    self.change_pixmap_signal.emit(cv_crop)
                     
                elif a.get_cv_mode() == 4:  # detecting line segment
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_edge_ = cobit_opencv_lane_detect._detect_edges(cv_mask_)
                    cv_crop_ = cobit_opencv_lane_detect._region_of_interest(cv_edge_)  
                    line_segments = cobit_opencv_lane_detect._detect_line_segments(cv_crop_)
                    line_segment_image = cobit_opencv_lane_detect._display_lines(cv_img, line_segments)
                    self.change_pixmap_signal.emit(line_segment_image)
                    
                elif a.get_cv_mode() == 5:  # detecting line slope
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_edge_ = cobit_opencv_lane_detect._detect_edges(cv_mask_)
                    cv_crop_ = cobit_opencv_lane_detect._region_of_interest(cv_edge_)  
                    line_segments = cobit_opencv_lane_detect._detect_line_segments(cv_crop_)
                    line_segment_image = cobit_opencv_lane_detect._display_lines(cv_img, line_segments)
                    lane_lines = cobit_opencv_lane_detect._average_slope_intercept(cv_img, line_segments)
                    lane_lines_image = cobit_opencv_lane_detect._display_lines(cv_img, lane_lines)
                    self.change_pixmap_signal.emit(lane_lines_image)

                elif a.get_cv_mode() == 6:  # draw steering angle 
                    cv_mask_ = cobit_opencv_lane_detect._get_mask(cv_img)
                    cv_edge_ = cobit_opencv_lane_detect._detect_edges(cv_mask_)
                    cv_crop_ = cobit_opencv_lane_detect._region_of_interest(cv_edge_)  
                    line_segments = cobit_opencv_lane_detect._detect_line_segments(cv_crop_)
                    line_segment_image = cobit_opencv_lane_detect._display_lines(cv_img, line_segments)
                    lane_lines = cobit_opencv_lane_detect._average_slope_intercept(cv_img, line_segments)
                    lane_lines_image = cobit_opencv_lane_detect._display_lines(cv_img, lane_lines)
                    new_steering_angle = cobit_opencv_lane_detect._compute_steering_angle(lane_lines_image, lane_lines)
                    self.curr_steering_angle = cobit_opencv_lane_detect._stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))
                    curr_heading_img = cobit_opencv_lane_detect._display_heading_line(lane_lines_image, self.curr_steering_angle)
                    self.change_pixmap_signal.emit(curr_heading_img)

                else:
                    self.change_pixmap_signal.emit(cv_img)
                    #lane, line_img = cobit_opencv_lane_detect._detect_lane(cv_img)
                    #new_steering_angle = cobit_opencv_lane_detect._compute_steering_angle(line_img, lane)
                    #self.curr_steering_angle = cobit_opencv_lane_detect._stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane))
                    #curr_heading_img = cobit_opencv_lane_detect._display_heading_line(line_img, self.curr_steering_angle)
                    #self.change_pixmap_signal.emit(curr_heading_img)
        
        # shut down capture system
        self.cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class App(QWidget):
    def __init__(self):
        super().__init__()

        '''
            deeptcar module initialize
        '''
        self.flag =False
        self.cv_mode = 0
        self.motor = CobitCarMotorL9110()
        self.servo = ServoKit(channels=16)

        '''
            Window layout 
        '''
        self.setGeometry(100,100, 800, 800)
        self.setWindowTitle("Deeptcar Operation Demo")
       

        # buttons - DC motor test
        self.motor_test_btn = QPushButton(self)
        self.motor_test_btn.setText("DC motor test")
        self.motor_test_btn.clicked.connect(self.test_DC_motor)
        self.motor_test_btn.setToolTip("Testing DC geared motor on-off 3 times")

        # buttons - set steering servo at center 
        self.servo_center_btn = QPushButton(self)
        self.servo_center_btn.setText("steering wheel center")
        self.servo_center_btn.clicked.connect(self.servo_to_center)
        self.servo_center_btn.setToolTip("Adjusting steering wheel to center")

        # buttons - servo motor test 
        self.servo_test_btn = QPushButton(self)
        self.servo_test_btn.setText("servo motor test")
        self.servo_test_btn.clicked.connect(self.test_servo_motor)
        self.servo_test_btn.setToolTip("Testing servo motor on-off 3 times")

        # servo trim control
        self.servo_trim_sld = QSlider(Qt.Horizontal, self)
        #self.servo_trim_sld.setFocusPolicy(Qt.NoFocus)
        self.servo_trim_sld.setGeometry(30, 40, 200, 30)
        self.servo_trim_sld.valueChanged[int].connect(self.sld_change_value)

        # buttons - start video thread  
        #self.video_start_btn = QPushButton(self)
        #self.video_start_btn.setText("starting OpenCV")
        #self.video_start_btn.clicked.connect(self.test_start_opencv)
        #self.video_start_btn.setToolTip("Testing openCV PI camera ")

        # buttons - stop video thread  
        #self.video_stop_btn = QPushButton(self)
        #self.video_stop_btn.setText("stop OpenCV")
        #self.video_stop_btn.clicked.connect(self.test_stop_opencv)
        #self.video_stop_btn.setToolTip("Testing openCV PI camera ")

        # radio botton
        self.radio_normal = QRadioButton("Normal camera view", self)
        self.radio_normal.setChecked(True)
        self.radio_normal.clicked.connect(self.cv_normal) 
        self.radio_mask = QRadioButton("Red color masking", self)
        self.radio_mask.setChecked(False)
        self.radio_mask.clicked.connect(self.cv_mask)
        self.radio_edge = QRadioButton("Canny edge detect", self)
        self.radio_edge.setChecked(False)
        self.radio_edge.clicked.connect(self.cv_canny)
        self.radio_crop = QRadioButton("Crop necessary region")
        self.radio_crop.setChecked(False)
        self.radio_crop.clicked.connect(self.cv_crop)
        self.radio_detect_line = QRadioButton("Detect line segments")
        self.radio_detect_line.setChecked(False)
        self.radio_detect_line.clicked.connect(self.cv_detect)
        self.radio_slope_lane = QRadioButton("Get lane slope")
        self.radio_slope_lane.setChecked(False)
        self.radio_slope_lane.clicked.connect(self.cv_slope)
        self.radio_draw_steering = QRadioButton("Draw steering angle")
        self.radio_draw_steering.setChecked(False)
        self.radio_draw_steering.clicked.connect(self.cv_steering)
        
        self.textLabel = QLabel('Deetcar Camera View')
        # create the label that holds the image
        self.disply_width = 320
        self.display_height = 240
        self.image_label = QLabel(self)
        self.image_label.move(0, 0)
        self.image_label.resize(self.disply_width, self.display_height)

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.motor_test_btn)
        vbox.addWidget(self.servo_center_btn)
        vbox.addWidget(self.servo_trim_sld)
        vbox.addWidget(self.servo_test_btn)
        #vbox.addWidget(self.video_start_btn)
        #vbox.addWidget(self.video_stop_btn)
        vbox.addWidget(self.radio_normal)
        vbox.addWidget(self.radio_mask)
        vbox.addWidget(self.radio_edge)
        vbox.addWidget(self.radio_crop)
        vbox.addWidget(self.radio_detect_line)
        vbox.addWidget(self.radio_slope_lane)
        vbox.addWidget(self.radio_draw_steering)        
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def get_cv_mode(self):
        return self.cv_mode

    def cv_normal(self):
        self.cv_mode = 0

    def cv_mask(self):
        self.cv_mode = 1

    def cv_canny(self):
        self.cv_mode = 2

    def cv_crop(self):
        self.cv_mode = 3

    def cv_detect(self):
        self.cv_mode = 4

    def cv_slope(self):
        self.cv_mode = 5

    def cv_steering(self):
        self.cv_mode = 6  

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def sld_change_value(self, value):
        print(value)

    def test_DC_motor(self):
        print("test DC motor")
        for i in range(3):
            print("%d time test",i)
            self.motor.motor_move_forward(50)
            time.sleep(2)
            self.motor.motor_stop()
            time.sleep(1)
        print("test is completed")

    def servo_to_center(self):
        print("move servo to center")
        servo_offset = 0
        self.servo.servo[0].angle = 90 + servo_offset

    def test_servo_motor(self):
        print("test servo motor")
        servo_offset = 0
        for i in range(3):
            print("%d time test",i)
            self.servo.servo[0].angle = 90 + servo_offset
            time.sleep(1)
            self.servo.servo[0].angle = 30 + servo_offset
            time.sleep(1)
            self.servo.servo[0].angle = 90 + servo_offset
            time.sleep(1)
            self.servo.servo[0].angle = 150 + servo_offset
            time.sleep(1)
            self.servo.servo[0].angle = 90 + servo_offset
        print("test is completed")

    #def test_start_opencv(self):
    #    print("starting openCV and pi camera")
    #    self.thread.set_flag_true()

    #def test_stop_opencv(self):
    #    print("stoping openCV and pi camera")
    #    self.thread.set_flag_false()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
     
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())