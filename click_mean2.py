#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Caculate mean rotation speed.
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
from ui_click_mean2 import Ui_MainWindow

import sys
import tables
import os
import csv
import numpy as np
import matplotlib.ticker as ticker
import scipy.signal


def smooth(x, window_len=11, window='hanning'):
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning',\
 'hamming', 'bartlett', 'blackman'")

    s = np.r_[2 * x[0] - x[window_len:1:-1],
              x,
              2 * x[-1] - x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


def format_min(x, pos=None):
    min = x // 60
    sec = x % 60
    return u"%d:%02d" % (min, sec)


class BacteriaModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(BacteriaModel, self).__init__(parent)
        self.dataset = []
        self.headers = ['start', 'stop', '<v>', '<v2>', '<vfft>']
        self.column_data = ['start', 'stop', 'v', 'v2', 'vfft']

    def index(self, row, column, parent):
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if parent.isValid():
            return 0
        else:
            return len(self.dataset)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        c = self.column_data[index.column()]
        r = index.row()
        data = self.dataset[r][c]
        if c == 'start' or c == 'stop':
            data = format_min(data)
        else:
            data = u'%.2f' % data
        return data

    def append(self, data):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.dataset),
                             len(self.dataset))
        self.dataset.append(data)
        self.endInsertRows()

    def remove(self, row):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.dataset.pop(row)
        self.endRemoveRows()

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self.headers[section]
        else:
            return None


class Application(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
#        Ui_MainWindow.__init__(self)
#        uic.loadUi(uifile, self)
        self.setupUi(self)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setModel(BacteriaModel())
        for ii in range(5):
            self.treeWidget.setColumnWidth(ii, 45)
        self.treeWidget.setMinimumWidth(210)
#        self.treeWidget.setMaximumWidth(240)
#        print self.treeWidget.width()
        self.last_clicked = None
        self.changed = False

    def connect_signals(self):
        self.Button_Add.clicked.connect(self.on_button_add_clicked)
        self.Button_Delete.clicked.connect(self.on_button_del_clicked)
        self.Button_Back.clicked.connect(self.on_button_previous_clicked)
        self.Button_Forward.clicked.connect(self.on_button_next_clicked)
        self.actionOpen.triggered.connect(self.on_open_menu)
        self.actionSave.triggered.connect(self.on_save_menu)
        self.action_About_Click_and_Mean.triggered.connect(self.on_about_menu)

    def closeEvent(self, event):
        if self.changed:
            query = "Your work has not been saved<p>Are you sure to quit?"
            reply = QtWidgets.QMessageBox.question(self, 'Quitting...',
                                               query,
                                               QtWidgets.QMessageBox.StandardButton.Yes,
                                               QtWidgets.QMessageBox.StandardButton.No)

            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def prepare_axis(self):
        self.figure = self.mpl.canvas.fig

        # setup matplotlib stuff on first notebook page (empty graph)
        self.ax_phase = self.figure.add_subplot(211)
        self.ax_phase.grid(True)
        self.ax_spec = self.figure.add_subplot(212, sharex=self.ax_phase,
                                               sharey=self.ax_phase)
        self.ax_spec.grid(True)
        self.canvas = self.mpl.canvas
        self.canvas.show()

    def get_open_filename(self):
        types = "HDF5 Files (*.h5);;TXT files (*.txt)"
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     "Open File",
                                                     QtCore.QDir.currentPath(),
                                                     types)
        if filename:
            return str(filename)
        else:
            return None

    def on_open_menu(self):
        self.filename = self.get_open_filename()
        if self.filename:
            self.load_file(self.filename)
            self.set_bacteria(0)

    def on_save_menu(self):
        default = os.path.splitext(os.path.split(self.filename)[1])[0] + '.csv'
        file_save = self.get_save_filename(os.path.dirname(self.filename),
                                           default)
        if file_save == None:
            return
        writer = csv.writer(open(file_save, 'w'))
        writer.writerow([os.path.split(self.filename)[1]])
        writer.writerow(['Bact.', 'start', 'stop', 'dt', 'v', 'v2', 'vfft',
                         'start', 'stop'])
        for m in self.models:
            for data in m.dataset:
                writer.writerow([data['bacteria'],
                                 data['start'],
                                 data['stop'],
                                 data['dt'],
                                 data['v'],
                                 data['v2'],
                                 data['vfft'],
                                 format_min(data['start']),
                                 format_min(data['stop'])])
        self.changed = False

    def get_save_filename(self, directory, filename):
        filesave, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     "Save File",
                                                     directory,
                                                     "CSV Files (*.csv)")
        if filesave:
            return filesave
        else:
            return None

    def load_file(self, filename):
        try:
            f = tables.open_file(filename, 'r')
            self.IQ = f.root.IQ.read()
            print(self.IQ.shape)
            self.FPS = f.root.FPS.read()
            self.nb_bacteria = self.IQ.shape[0]
            f.close()
            self.filetype = 'H5'
        except IOError:
            data = np.loadtxt(filename, skiprows=1, unpack=True)
            self.FPS = 50
            self.nb_bacteria = (data.shape[0] - 1) / 2
            self.IQ = np.empty((self.nb_bacteria, data.shape[1], 2))
            for ii in range(self.nb_bacteria):
                self.IQ[ii, :, 0] = np.cos(data[2 * ii + 2] / 180. * np.pi)
                self.IQ[ii, :, 1] = np.sin(data[2 * ii + 2] / 180. * np.pi)
            self.filetype = 'TXT'
        self.models = []
        for ii in range(self.nb_bacteria):
            self.models.append(BacteriaModel())
        self.changed = False

    def set_bacteria(self, index):
        self.index = index
        self.label.setText("%d/%d" % (index, self.nb_bacteria - 1))
        self.xc = self.IQ[index, :, 0] + 1j * self.IQ[index, :, 1]
        self.xc = self.xc - np.mean(self.xc)
        if self.filetype == 'TXT':
            # To be checked !
            a, b = scipy.signal.butter(4, [0.01, 0.95], 'bandpass')
            self.xc = scipy.signal.filtfilt(a, b, self.xc)
        ph = np.unwrap(np.angle(self.xc))
        self.time = np.arange(len(ph), dtype=float) / self.FPS
        fact = self.FPS / 2. / np.pi
        self.vit_phase = fact * np.diff(ph)
        self.vit_phase_smooth = fact * smooth(np.diff(ph), self.FPS)
        self.ax_phase.clear()
        self.ax_phase.plot(self.time[:-1],
                           self.vit_phase)
        self.ax_phase.plot(self.time[:-1],
                           self.vit_phase_smooth,
                           lw=2)
        self.ax_phase.grid(True)
        self.ax_phase.set_title("%s / %d" % (os.path.basename(self.filename),
                                             self.index))
        self.ax_phase.set_ylabel('Rotation speed (Hz)')
        self.ax_spec.clear()
        self.ax_spec.specgram(self.xc, NFFT=128, Fs=self.FPS, noverlap=0)
        self.ax_spec.xaxis.set_major_formatter(\
            ticker.FuncFormatter(format_min))
        self.ax_spec.grid(True)
        self.ax_spec.set_ylabel('Rotation speed (Hz)')
        self.ax_spec.set_xlabel('time (min:s)')

        self.canvas.draw()
        if index == 0:
            self.Button_Back.setEnabled(False)
        else:
            self.Button_Back.setEnabled(True)
        if index == (self.nb_bacteria - 1):
            self.Button_Forward.setEnabled(False)
        else:
            self.Button_Forward.setEnabled(True)
        self.treeWidget.setModel(self.models[index])

    def on_click(self, event):
        if self.last_clicked:
            self.canvas.mpl_disconnect(self.connection)
            ind1, ind2 = np.searchsorted(self.time,
                                         [self.last_clicked, event.xdata])
            if ind1 > ind2:
                QtWidgets.QMessageBox.warning(\
                    self, u'Invalid input',
                    u'Your second point is before your first point!')
            else:
                xc_loc = self.xc[ind1:ind2]
                xc_loc = xc_loc - np.mean(xc_loc)
                vmean = np.mean(self.vit_phase[ind1:ind2])
                vmean2 = np.mean(self.FPS / 2. / np.pi *
                                 np.diff(np.unwrap(np.angle(xc_loc))))
                fft = np.abs(np.fft.fft(xc_loc))
                vit = np.fft.fftfreq(len(fft), 1. / self.FPS)
                vmean3 = vit[np.argmax(fft)]
                data = {'start': self.last_clicked,
                        'stop': event.xdata,
                        'dt': event.xdata - self.last_clicked,
                        'v': vmean,
                        'v2': vmean2,
                        'vfft': vmean3,
                        'bacteria': self.index}
                self.models[self.index].append(data)

            for widget in [self.Button_Add, self.Button_Delete,
                           self.treeWidget]:
                widget.setEnabled(True)
            self.last_clicked = None
        else:
            self.last_clicked = event.xdata
        self.changed = True

    def on_button_add_clicked(self):
        for widget in [self.Button_Add, self.Button_Delete, self.treeWidget]:
            widget.setEnabled(False)

        self.connection = self.canvas.mpl_connect('button_press_event',
                                                  self.on_click)

    def on_button_del_clicked(self):
        selected = self.treeWidget.selectedIndexes()
        for ind in selected:
            if ind.column() == 0:
                self.models[self.index].remove(ind.row())
        self.changed = True

    def on_button_next_clicked(self):
        if (self.index + 1) < self.nb_bacteria:
            self.set_bacteria(self.index + 1)

    def on_button_previous_clicked(self):
        if self.index > 0:
            self.set_bacteria(self.index - 1)

    def on_about_menu(self):
        QtWidgets.QMessageBox.about(self, "About Click and Mean",
                                "<p><b>Click and Mean</b></p>"
                                "<p>Bacteria rotation analysis</p>"
                                "<p><em>(c) 2010 Antoine Sirinelli</em></p>")
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_app = Application()
    my_app.connect_signals()
    my_app.prepare_axis()
    my_app.show()
    sys.exit(app.exec())
