import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import cobit_opencv_lane_detect

from_class = uic.loadUiType("getting_started.ui")[0]

class MyWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()