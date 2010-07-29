#!/usr/bin/env python

from PyQt4 import QtGui, QtCore, uic
import sys
from opencv_bacteria import run_analysis
from plot_phase import plot_phase

app = QtGui.QApplication(sys.argv)

dialog = uic.loadUi('dialog.ui')
filename = QtGui.QFileDialog.getOpenFileName(None, "Open movie file...",
                                             QtCore.QDir.currentPath(),
                                             "Movie (*.avi)")
if not filename:
    sys.exit()
filename = str(filename)
dialog.setWindowTitle(filename)
if not dialog.exec_():
    sys.exit()
fps = int(dialog.lineEdit.text())


ret = QtGui.QMessageBox.question(None, "Configuration file",
                                 "Do you have a configuration file ?",
                                 QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                 QtGui.QMessageBox.No)
# msgBox = QtGui.QMessageBox()
# msgBox.setText("Do you have a configuration file ?")
# msgBox.setStandardButtons(msgBox.No | msgBox.Yes)
# ret = msgBox.exec_()
if ret == QtGui.QMessageBox.Yes:
    config_filename = QtGui.QFileDialog.getOpenFileName(None,
                                                        "Open configuration file",
                                                        QtCore.QFileInfo(filename).path(),
                                                        "Configuration file (*.txt)")
    config_filename = str(config_filename)
else:
    config_filename = None

# msgBox = QtGui.QMessageBox()
# msgBox.setText("Please Wait....")
# msgBox.setWindowTitle("Work in Progress")
# msgBox.show()


h5file = run_analysis(filename, fps, config_filename)
plot_phase(h5file)
# msgBox.close()
app.exec_()
