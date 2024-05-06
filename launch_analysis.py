#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script to launch the video analyser.
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

from PyQt6 import QtCore, QtWidgets
import sys
from opencv_bacteria import run_analysis
from plot_phase import plot_phase

app = QtWidgets.QApplication(sys.argv)

filename, filetype = QtWidgets.QFileDialog.getOpenFileName(None, "Open movie file...",
                                             QtCore.QDir.currentPath(),
                                             "Movie (*.avi)")
if not filename:
    sys.exit()
filename = str(filename)


class dialog_FPS(QtWidgets.QDialog):
    def __init__(self, title):
        QtWidgets.QDialog.__init__(self)
        verticalLayout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Please enter the Frames-per-Second value used")
        verticalLayout.addWidget(label)
        self.lineEdit = QtWidgets.QLineEdit()
        verticalLayout.addWidget(self.lineEdit)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel |
                                     QtWidgets.QDialogButtonBox.StandardButton.Ok)
        verticalLayout.addWidget(buttonBox)
        self.setLayout(verticalLayout)
        self.setWindowTitle(title)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.lineEdit.returnPressed.connect(self.accept)


class dialog_help(QtWidgets.QDialog):
    def __init__(self, text):
        QtWidgets.QDialog.__init__(self)
        verticalLayout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(text)
        verticalLayout.addWidget(label)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        verticalLayout.addWidget(buttonBox)
        self.setLayout(verticalLayout)
        self.setWindowTitle("Help")
        buttonBox.accepted.connect(self.accept)


dialog = dialog_FPS(filename)
if not dialog.exec():
    sys.exit()
fps = int(dialog.lineEdit.text())


ret = QtWidgets.QMessageBox.question(None, "Configuration file",
                                 "Do you have a configuration file ?",
                                 QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Yes,
                                 QtWidgets.QMessageBox.StandardButton.No)

if ret == QtWidgets.QMessageBox.StandardButton.Yes:
    config_filename, filetype = \
        QtWidgets.QFileDialog.getOpenFileName(None,
                                          "Open configuration file",
                                          QtCore.QFileInfo(filename).path(),
                                          "Configuration file (*.txt)")
    config_filename = str(config_filename)
else:
    config_filename = None

help_text = """<b>Keys used for video analysis</b><br>
<b>+</b>/<b>-</b>: change the window size<br>
<b>[left]</b>/<b>[right]</b>/<b>[up]</b/>/<b>[down]</b>: move the window<br>
<b>[space]</b>: select current window for analysis<br>
<b>[backspace]</b>: remove previously selected window<br>
<b>g</b>/<b>t</b>: change the contrast threshold<br>
<b>z</b>, <b>x</b>, <b>c</b>, <b>v</b>: jump to start, 25%, 50%, 75%<br>
<b>q</b>: launch the analysis<br>
"""

help = dialog_help(help_text)
help.show()

h5file = run_analysis(filename, fps, config_filename)
plot_phase(h5file)
app.exec()
