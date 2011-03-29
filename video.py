#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Frame by frame video analyser. Can also display analysis windows.
# Copyright (C) 2010-2011 Antoine Sirinelli
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import SIGNAL
import sys
import cv
import Image
import tables
import os
from ImageQt import ImageQt
import numpy as np
from ui_video import Ui_MainWindow


FONT = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5)


def format_min(x, pos=None):
    min = x // 60
    sec = x % 60
    return u"%d:%05.2f" % (min, sec)


def window_placement(image, x, y, width, height, color, nb=None, pos=None):
    cv.Rectangle(image, (x, y), (x + width, y + height),
                 color, 1, 8, 0)
    if nb is not None:
        cv.PutText(image, '%0d' % nb, (x + width + 2, y + height / 2),
                   FONT, color)
    if pos is not None:
        cv.Circle(image, (x + int(round(pos[0])),
                          y + int(round(pos[1]))), 2, color, -1)


class Application(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.capture = None
        self.image = None

    def connect_signals(self):
        self.connect(self.actionOpen, SIGNAL("triggered()"),
                     self.on_open_menu)
        self.connect(self.actionSave, SIGNAL("triggered()"),
                     self.on_save_menu)
        self.connect(self.actionAbout, SIGNAL("triggered()"),
                     self.on_about_menu)
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
            self.nb_frames = \
                cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT)
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(self.nb_frames - 1)
            self.fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
        else:
            return
        filename = \
            QtGui.QFileDialog.getOpenFileName(self,
                                              "Open Data file",
                                              os.path.dirname(str(filename)),
                                              "H5 Files (*.h5)")
        if filename:
            f = tables.openFile(str(filename), 'r')
            self.windows = f.root.windows.read()
            self.fps = f.root.FPS.read()
            # self.IQ = f.root.IQ.read()
            f.close()
        else:
            self.windows = []

        self.time = np.arange(self.nb_frames, dtype=float) / self.fps
        self.update_frame(0)

    def on_save_menu(self):
        if self.image is None:
            return
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save current image",
                                                     QtCore.QDir.currentPath(),
                                                     "PNG Files (*.png)")
        if filename:
            self.image.save(filename)

    def update_frame(self, index):
        if self.capture == None:
            return
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, index)
        frame = cv.QueryFrame(self.capture)
        for w in self.windows:
            window_placement(frame, w['x'], w['y'], w['width'], w['height'],
                             cv.CV_RGB(0, 255, 0), w['id'])
                             # (self.IQ[w['id'],index,0],
                             #  self.IQ[w['id'],index,0]) )

        im = Image.fromstring("RGB", (frame.width, frame.height),
                              frame.tostring())
        image = ImageQt(im)
        self.image = image.copy()  # Bug in Windows
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.image))
        self.label.adjustSize()
        t = self.time[index]
        self.label_2.setText(format_min(t) + " / %d" % index)

    def next_frame(self):
        index = self.horizontalSlider.value()
        index = index + 1
        self.horizontalSlider.setValue(index)

    def previous_frame(self):
        index = self.horizontalSlider.value()
        index = index - 1
        self.horizontalSlider.setValue(index)

    def on_about_menu(self):
        QtGui.QMessageBox.about(self, "About this video player",
                                "<p><b>Video player</b></p>"
                                "<p><em>(c) 2011 Antoine Sirinelli</em></p>"
                                "<p>Distributed under GNU GPL v2+</p>")
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    my_app = Application()
    my_app.connect_signals()
    my_app.show()
    sys.exit(app.exec_())
