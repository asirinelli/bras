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

from PyQt6 import QtWidgets, QtCore, QtGui
import sys
import cv2 as cv
import tables
import os
import numpy as np
from ui_video import Ui_MainWindow


def format_min(x, pos=None):
    min = x // 60
    sec = x % 60
    return u"%d:%05.2f" % (min, sec)


def window_placement(image, x, y, width, height, color, nb=None, pos=None):
    cv.rectangle(image, (x, y), (x + width, y + height),
                 color, 1, 8, 0)
    if nb != None:
        cv.putText(image, '%0d' % nb, (int(x + width + 2), int(y + height / 2)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, color)
    if pos is not None:
        cv.circle(image, (x + int(round(pos[0])),
                          y + int(round(pos[1]))), 2, color, -1)


class Application(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.capture = None
        self.image = None

    def connect_signals(self):
        self.actionOpen.triggered.connect(self.on_open_menu)
        self.actionSave.triggered.connect(self.on_save_menu)
        self.actionAbout.triggered.connect(self.on_about_menu)
        self.horizontalSlider.valueChanged.connect(self.update_frame)
        self.button_next.clicked.connect(self.next_frame)
        self.button_previous.clicked.connect(self.previous_frame)

    def on_open_menu(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     "Open Movie File",
                                                     QtCore.QDir.currentPath(),
                                                     "AVI Files (*.avi)")
        if filename:
            self.capture = cv.VideoCapture(str(filename))
            self.nb_frames = int(self.capture.get(cv.CAP_PROP_FRAME_COUNT))
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(self.nb_frames - 1)
            self.fps = self.capture.get(cv.CAP_PROP_FRAME_COUNT)
        else:
            return
        filename, filetype = \
            QtWidgets.QFileDialog.getOpenFileName(self,
                                              "Open Data file",
                                              os.path.dirname(str(filename)),
                                              "H5 Files (*.h5)")
        if filename:
            f = tables.open_file(str(filename), 'r')
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
        filename, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     "Save current image",
                                                     QtCore.QDir.currentPath(),
                                                     "PNG Files (*.png)")
        if filename:
            self.image.save(filename)

    def update_frame(self, index):
        if self.capture == None:
            return
        self.capture.set(cv.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.capture.read()
        for w in self.windows:
            window_placement(frame, w['x'], w['y'], w['width'], w['height'],
                             (0, 255, 0), w['id'])
                             # (self.IQ[w['id'],index,0],
                             #  self.IQ[w['id'],index,0]) )

        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        self.image = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap(self.image))
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
        QtWidgets.QMessageBox.about(self, "About this video player",
                                "<p><b>Video player</b></p>"
                                "<p><em>(c) 2011 Antoine Sirinelli</em></p>"
                                "<p>Distributed under GNU GPL v2+</p>")
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_app = Application()
    my_app.connect_signals()
    my_app.show()
    sys.exit(app.exec())
