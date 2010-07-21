from PyQt4 import QtGui, uic, QtCore, Qt
from PyQt4.QtCore import SIGNAL
import sys, cv, Image, tables, os
from ImageQt import ImageQt
import numpy as np

def format_min(x, pos=None):
    min = x //60
    sec = x % 60
    return u"%d:%05.2f"%(min, sec)

FONT = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5)

def window_placement(image,x, y, width, height, color, nb=None):
    cv.Rectangle(image, (x, y), (x + width, y + height),
                   color, 1, 8, 0)
    if nb != None:
        cv.PutText(image, '%0d'%nb, (x+width+2, y+height/2),
                     FONT, color)


class Application(QtGui.QMainWindow):
    def __init__(self, uifile):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.capture = None

    def connect_signals(self):
        self.connect(self.actionOpen, SIGNAL("triggered()"),
                     self.on_open_menu)
        self.connect(self.horizontalSlider, SIGNAL("valueChanged(int)"),
                     self.update_frame)
        self.connect(self.button_next, SIGNAL("clicked()"),
                     self.next_frame)
        self.connect(self.button_previous, SIGNAL("clicked()"),
                     self.previous_frame)
        
    def on_open_menu(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     "Open Movie File",
                                                     QtCore.QDir.currentPath(),
                                                     "AVI Files (*.avi)")
        if filename:
            self.capture = cv.CreateFileCapture(str(filename))
            self.nb_frames = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(self.nb_frames-1)
            self.fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
        else:
            return
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     "Open Data file",
                                                     os.path.dirname(str(filename)),
                                                     "H5 Files (*.h5)")
        if filename:
            f = tables.openFile(str(filename), 'r')
            self.windows = f.root.windows.read()
            self.fps = f.root.FPS.read()
            f.close()
        else:
            self.windows = []

        self.time = np.arange(self.nb_frames, dtype=float)/self.fps
        self.update_frame(0)


    def update_frame(self, index):
        if self.capture == None:
            return
        frame = cv.QueryFrame(self.capture)
        for w in self.windows:
            window_placement(frame, w['x'], w['y'], w['width'], w['height'],
                             cv.CV_RGB(0, 255, 0), w['id'])

        im = Image.fromstring("RGB", (frame.width, frame.height),
                              frame.tostring())
        image = ImageQt(im)
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))
        self.label.adjustSize()
        t = self.time[index]
        self.label_2.setText(format_min(t) + " / %d"%index)
    def next_frame(self):
        index = self.horizontalSlider.value()
        index = index + 1
        self.horizontalSlider.setValue(index)
    def previous_frame(self):
        index = self.horizontalSlider.value()
        index = index - 1
        self.horizontalSlider.setValue(index)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    my_app = Application('video.ui')
    my_app.connect_signals()
    my_app.show()
    sys.exit(app.exec_())
