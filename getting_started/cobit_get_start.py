from PyQt5 import QtGui
from PyQt5.QtWidgets import * # QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
import time 
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from cobit_car_motor_l9110 import CobitCarMotorL9110
import cobit_deep_lane_detect
import cobit_opencv_lane_detect
from adafruit_servokit import ServoKit
from cobit_deep_lane_detect import CobitDeepLaneDetect



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
                    print(self.curr_steering_angle)
                    if self.curr_steering_angle < 160 and self.curr_steering_angle > 20:
                        a.servo_(self.curr_steering_angle)
                    else:
                        pass

                elif a.get_cv_mode() == 7: # deep driving 
                    angle_deep, img_angle = deep_detector.follow_lane(cv_img)
                    self.change_pixmap_signal.emit(img_angle)
                    if img_angle is None:
                        print("angle image out!!")
                        pass
                    else:
                        print(angle_deep)
                        if angle_deep < 160 and angle_deep > 20:
                            a.servo_(angle_deep)
                        else:
                            pass

                else:
                    self.change_pixmap_signal.emit(cv_img)
                   
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
        self.servo_offset = 0
        self.cv_throttle = 0
        self.dp_throttle = 0
        self.driveFlag = False

        '''
            Window layout 
        '''
        #elf.setGeometry(100,100, 800, 800)
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
        self.servo_trim_label = QLabel('0', self)
        self.servo_trim_label.setAlignment(Qt.AlignCenter )
        self.servo_trim_label.setMinimumWidth(100)
        self.servo_trim_label.setText("0")
        self.servo_trim_sld = QSlider(Qt.Horizontal, self)
        self.servo_trim_sld.setRange(-20, 20)
        self.servo_trim_sld.valueChanged[int].connect(self.sld_change_value)

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
        self.radio_deep_steering = QRadioButton("Draw deep steering angle")
        self.radio_deep_steering.setChecked(False)
        self.radio_deep_steering.clicked.connect(self.cv_deep_steering)       
        # create the label that holds the image
        self.disply_width = 320
        self.display_height = 240
        self.image_label = QLabel(self)
        self.image_label.move(0, 0)
        self.image_label.resize(self.disply_width, self.display_height)

        # buttons - OpenCV lane driving 
        self.cv_lane_drive_start_btn = QPushButton(self)
        self.cv_lane_drive_start_btn.setText("OpenCV lane detect driving start")
        self.cv_lane_drive_start_btn.clicked.connect(self.opencv_lane_drive_start)
        self.cv_lane_drive_start_btn.setToolTip("OpenCV lane detecting driving start")

        # buttons - OpenCV lane driving 
        self.cv_lane_drive_stop_btn = QPushButton(self)
        self.cv_lane_drive_stop_btn.setText("OpenCV lane detect driving stop")
        self.cv_lane_drive_stop_btn.clicked.connect(self.opencv_lane_drive_stop)
        self.cv_lane_drive_stop_btn.setToolTip("OpenCV lane detecting driving stop")

        # buttons - Deep lane driving 
        self.dp_lane_drive_start_btn = QPushButton(self)
        self.dp_lane_drive_start_btn.setText("Deep learning lane detect driving start")
        self.dp_lane_drive_start_btn.clicked.connect(self.deep_lane_drive_start)
        self.dp_lane_drive_start_btn.setToolTip("Deep leanring lane detecting driving start")

        # buttons - Deep lane driving 
        self.dp_lane_drive_stop_btn = QPushButton(self)
        self.dp_lane_drive_stop_btn.setText("Deep learning lane detect driving stop")
        self.dp_lane_drive_stop_btn.clicked.connect(self.deep_lane_drive_stop)
        self.dp_lane_drive_stop_btn.setToolTip("Deep learning lane detecting driving stop")

        # cv throttle control
        self.sld_cv_throttle = QSlider(Qt.Horizontal, self)
        self.sld_cv_throttle.setRange(0, 50)
        self.sld_cv_throttle.valueChanged[int].connect(self.sld_cv_throttle_value)

        # deep throttle label
        self.cv_throttle_label = QLabel('0', self)
        self.cv_throttle_label.setAlignment(Qt.AlignCenter )
        self.cv_throttle_label.setMinimumWidth(100)
        self.cv_throttle_label.setText("0")

        # dp throttle control
        self.sld_dp_throttle = QSlider(Qt.Horizontal, self)
        self.sld_dp_throttle.setRange(0, 50)
        self.sld_dp_throttle.valueChanged[int].connect(self.sld_dp_throttle_value)

        # deep throttle label
        self.deep_throttle_label = QLabel('0', self)
        self.deep_throttle_label.setAlignment(Qt.AlignCenter )
        self.deep_throttle_label.setMinimumWidth(100)
        self.deep_throttle_label.setText("0")

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        h_cv_box = QHBoxLayout()
        v_cv_radio_box = QVBoxLayout() 
        v_cv_motor_box = QVBoxLayout()
        v_cv_throttle_box = QVBoxLayout()
        h_cv_motor_throttle_box = QHBoxLayout()
        v_dp_motor_box = QVBoxLayout()
        v_dp_throttle_box = QVBoxLayout()
        h_dp_motor_throttle_box = QHBoxLayout()
        vbox.addWidget(self.motor_test_btn)
        vbox.addWidget(self.servo_center_btn)
        hbox.addWidget(self.servo_trim_label)
        hbox.addWidget(self.servo_trim_sld)
        vbox.addLayout(hbox)
        vbox.addWidget(self.servo_trim_sld)
        vbox.addWidget(self.servo_test_btn)
        v_cv_radio_box.addWidget(self.radio_normal)
        v_cv_radio_box.addWidget(self.radio_mask)
        v_cv_radio_box.addWidget(self.radio_edge)
        v_cv_radio_box.addWidget(self.radio_crop)
        v_cv_radio_box.addWidget(self.radio_detect_line)
        v_cv_radio_box.addWidget(self.radio_slope_lane)
        v_cv_radio_box.addWidget(self.radio_draw_steering)   
        v_cv_radio_box.addWidget(self.radio_deep_steering)     
        h_cv_box.addLayout(v_cv_radio_box)
        h_cv_box.addWidget(self.image_label)
        vbox.addLayout(h_cv_box)  
        v_cv_motor_box.addWidget(self.cv_lane_drive_start_btn)
        v_cv_motor_box.addWidget(self.cv_lane_drive_stop_btn)
        v_cv_throttle_box.addWidget(self.sld_cv_throttle)
        v_cv_throttle_box.addWidget(self.cv_throttle_label)
        h_cv_motor_throttle_box.addLayout(v_cv_motor_box)
        h_cv_motor_throttle_box.addLayout(v_cv_throttle_box)
        v_dp_motor_box.addWidget(self.dp_lane_drive_start_btn)
        v_dp_motor_box.addWidget(self.dp_lane_drive_stop_btn)
        v_dp_throttle_box.addWidget(self.sld_dp_throttle)
        v_dp_throttle_box.addWidget(self.deep_throttle_label)
        h_dp_motor_throttle_box.addLayout(v_dp_motor_box)
        h_dp_motor_throttle_box.addLayout(v_dp_throttle_box)
        vbox.addLayout(h_cv_motor_throttle_box)
        vbox.addLayout(h_dp_motor_throttle_box)
        vbox.addWidget(self.dp_lane_drive_start_btn)
        vbox.addWidget(self.dp_lane_drive_stop_btn)
        
        
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

    def cv_deep_steering(self):
        self.cv_mode = 7  

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def sld_change_value(self, value):
        self.servo_trim_label.setText(str(value))
        self.servo_offset = value
        self.servo.servo[0].angle = 90+value

    def sld_cv_throttle_value(self, value):
        self.cv_throttle = value
        self.cv_throttle_label.setText(str(value))
        if self.driveFlag is True:
            self.motor.motor_move_forward(self.cv_throttle)
        else:
            self.motor.motor_move_forward(0)

    def sld_dp_throttle_value(self, value):
        self.dp_throttle = value
        self.deep_throttle_label.setText(str(value))
        if self.driveFlag is True:
            self.motor.motor_move_forward(self.dp_throttle)
        else:
            self.motor.motor_move_forward(0)

    def servo_(self, angle):
        self.servo.servo[0].angle = angle+self.servo_offset

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
        self.servo.servo[0].angle = 90

    def test_servo_motor(self):
        print("test servo motor")
        for i in range(3):
            print("%d time test",i)
            self.servo.servo[0].angle = 90
            time.sleep(1)
            self.servo.servo[0].angle = 30
            time.sleep(1)
            self.servo.servo[0].angle = 90
            time.sleep(1)
            self.servo.servo[0].angle = 150
            time.sleep(1)
            self.servo.servo[0].angle = 90
        print("test is completed")

    def opencv_lane_drive_start(self):
        self.driveFlag = True
        self.cv_mode = 6
        self.motor.motor_move_forward(self.cv_throttle)
        self.radio_draw_steering.setChecked(True)
        print("CV drive start")
    
    def opencv_lane_drive_stop(self):
        self.driveFlag = False
        self.motor.motor_move_forward(0) 
        self.radio_draw_steering.setChecked(False)
        self.radio_normal.setChecked(True)
        self.cv_mode = 0
        print("CV drive stop")

    def deep_lane_drive_start(self):
        self.driveFlag = True
        self.cv_mode = 7
        self.motor.motor_move_forward(self.dp_throttle)
        self.radio_deep_steering.setChecked(True)
        print("deep drive start")
    
    def deep_lane_drive_stop(self):
        self.driveFlag = False
        self.cv_mode = 0
        self.motor.motor_move_forward(0)
        self.radio_deep_steering.setChecked(False)
        self.radio_normal.setChecked(True)
        print("deep drive start")     
    

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
    deep_detector = CobitDeepLaneDetect("/home/pi/deepThinkCar/models/lane_navigation_final.h5")
    a = App()
    a.show()
    sys.exit(app.exec_())