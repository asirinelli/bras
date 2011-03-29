#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import sys
from opencv_bacteria import run_analysis
from plot_phase import plot_phase
from ui_dialog import Ui_FPS
app = QtGui.QApplication(sys.argv)

filename = QtGui.QFileDialog.getOpenFileName(None, "Open movie file...",
                                             QtCore.QDir.currentPath(),
                                             "Movie (*.avi)")
if not filename:
    sys.exit()
filename = str(filename)

class dialog_FPS(QtGui.QDialog):
    def __init__(self, title):
        QtGui.QDialog.__init__(self)
        verticalLayout = QtGui.QVBoxLayout()
        label = QtGui.QLabel("Please enter the Frames-per-Second value used")
        verticalLayout.addWidget(label)
        self.lineEdit = QtGui.QLineEdit()
        verticalLayout.addWidget(self.lineEdit)
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | 
                                     QtGui.QDialogButtonBox.Ok)
        verticalLayout.addWidget(buttonBox)
        self.setLayout(verticalLayout)
        self.setWindowTitle(title)
        self.connect(buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        self.connect(self.lineEdit, QtCore.SIGNAL("returnPressed()"),
                     self.accept)

class dialog_help(QtGui.QDialog):
    def __init__(self, text):
        QtGui.QDialog.__init__(self)
        verticalLayout = QtGui.QVBoxLayout()
        label = QtGui.QLabel(text)
        verticalLayout.addWidget(label)
        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        verticalLayout.addWidget(buttonBox)
        self.setLayout(verticalLayout)
        self.setWindowTitle("Help")
        self.connect(buttonBox, QtCore.SIGNAL("accepted()"), self.accept)


dialog = dialog_FPS(filename)
if not dialog.exec_():
    sys.exit()
fps = int(dialog.lineEdit.text())


ret = QtGui.QMessageBox.question(None, "Configuration file",
                                 "Do you have a configuration file ?",
                                 QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                 QtGui.QMessageBox.No)

if ret == QtGui.QMessageBox.Yes:
    config_filename = QtGui.QFileDialog.getOpenFileName(None,
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
help.show();

h5file = run_analysis(filename, fps, config_filename)
plot_phase(h5file)
app.exec_()
