#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Analyse a video by finding the centre of bacteria.
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

import sys
import os
import time
import cv2 as cv
import numpy as np
import tables


# Keys used for the windows

STOP_INTERACTIVE = (113, 1048689)  # q
MOVE_LEFT = (65361, 2424832)
MOVE_UP = (65362, 2490368)
MOVE_RIGHT = (65363, 2555904)
MOVE_DOWN = (65364, 2621440)
DECREASE_WINDOW = (45, 1048621, 1114029)  # -
INCREASE_WINDOW = (43, 65579, 1114155, 1114027)  # +
INCREASE_THRESHOLD = (116, 1048692)  # t
DECREASE_THRESHOLD = (103, 1048679)  # g
SELECT_WINDOW = (32, 1048608)  # <space>
REMOVE_WINDOW = (8, 65288, 1113864)  # <backspace>
JUMP_TO_0 = (122, 119, 1048698)  # z or w
JUMP_TO_0_25 = (120, 1048696)  # x
JUMP_TO_0_50 = (99, 1048675)  # c
JUMP_TO_0_75 = (118, 1048694)  # v


class window:
    def __init__(self, x, y, width, height, threshold=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.threshold = threshold


class h5_window(tables.IsDescription):
    id = tables.UInt16Col()
    x = tables.UInt16Col()
    y = tables.UInt16Col()
    width = tables.UInt16Col()
    height = tables.UInt16Col()
    threshold = tables.UInt16Col()


def windows_to_h5(windows, table):
    row = table.row
    for ii, w in enumerate(windows):
        row['id'] = ii
        row['x'] = w.x
        row['y'] = w.y
        row['width'] = w.width
        row['height'] = w.height
        row['threshold'] = w.threshold
        row.append()


def save_config(windows, name):
    out = open(name, 'w')
    for w in windows:
        out.write('%d\t%d\t%d\t%d\t%d\n' %
                  (w.x, w.y, w.width, w.height, w.threshold))
    out.close()


def read_config(name):
    f = open(name, 'r')
    out = []
    for line in f:
        l = [int(ii) for ii in line.split()]
        out.append(window(*l))
    return out


def window_placement(image, x, y, width, height, color, nb=None):
    cv.rectangle(image, (x, y),
                 (x + width, y + height),
                 color, 1, 8, 0)
    if nb != None:
        cv.putText(image, '%0d' % nb, (int(x + width + 2), int(y + height / 2)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, color)


def get_IQ(capture, windows):
    nb_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
#  data = [np.empty((nb_frames, 2))]*len(windows)
    data = np.empty((len(windows), nb_frames, 2))
    crop_gray = []
    crop_rect = []
    matX = []
    matY = []
    for w in windows:
        #crop_gray.append(cv.CreateMat(w.height, w.width, cv.CV_8UC1))
        crop_gray.append(np.zeros((w.height, w.width), dtype=np.int8))
        crop_rect.append((w.x, w.y, w.width, w.height))
        mx, my = np.meshgrid(np.arange(w.width), np.arange(w.height))
        matX.append(mx)
        matY.append(my)

    cv.namedWindow('Monitor', cv.WINDOW_AUTOSIZE)

    for fi in range(nb_frames):
        ret, image = capture.read()
        for ii in range(len(windows)):
            crop2 = crop_gray[ii]
            wx1, wx2 = crop_rect[ii][0], crop_rect[ii][0] + crop_rect[ii][2]
            wy1, wy2 = crop_rect[ii][1], crop_rect[ii][1] + crop_rect[ii][3]
            crop = np.invert(image[wy1:wy2, wx1:wx2, 0])
            crop = (crop > windows[ii].threshold) * crop
            # cv.Threshold(crop2, crop2, windows[ii].threshold, 0,
            #              cv.CV_THRESH_TOZERO)
#      arr = np.asarray(crop2, dtype='int')#[:,:,0]
            # arr = np.fromstring(crop2.tostring(), dtype=np.uint8)
            # arr.resize((crop2.rows, crop2.cols))
#      matX, matY = np.meshgrid(range(arr.shape[0]),
#                               range(arr.shape[1]))

            M00 = np.sum(crop)
            if M00 == 0:
                print("No pixel found (frame: %d, window: %d)" % (fi, ii))
                M00 = 1
            M10 = np.sum(matX[ii] * crop)
            M01 = np.sum(matY[ii] * crop)
            X = float(M10) / float(M00)
            Y = float(M01) / float(M00)
#      data[ii][fi] = [X, Y]
            data[ii, fi] = np.array([X, Y])

        if fi % 1000 == 0:
            print(fi)
            for jj, w in enumerate(windows):
                window_placement(image, w.x, w.y, w.width, w.height,
                                 (255, 0, 0), jj)
            cv.putText(image, '%7d/%d' % (fi, nb_frames), (2, 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))
            cv.imshow('Monitor', image)
            cv.waitKey(10)

#    print M00, norm, M10, M01, X, Y
#    cv.cvCircle(crop, cv.cvPoint(int(X), int(Y)),
#                2, cv.CV_RGB(0, 255, 0), -1, 8, 0)
#    print A, B, C, D, X, Y
    cv.destroyWindow('Monitor')
    return data


def set_windows(capture, windows_list=[]):
    # create windows
    cv.namedWindow('Film', cv.WINDOW_AUTOSIZE)
    if windows_list:
        threshold = windows_list[-1].threshold
    else:
        threshold = 128
    x = 200
    y = 100
    height = 20
    width = 20
    cap_height = int(capture.get(cv.CAP_PROP_FRAME_HEIGHT))
    cap_width = int(capture.get(cv.CAP_PROP_FRAME_WIDTH))
    nb_frames = capture.get(cv.CAP_PROP_FRAME_COUNT)

#    frame_gray = cv.cvCreateMat(cap_height, cap_width, cv.CV_8UC1)
    while 1:
        # capture the current frame
        ret, frame = capture.read()
        if frame is None:
            capture.set(cv.CAP_PROP_POS_FRAMES, 0)
            ret, frame = capture.read()

        # cv.cvCvtColor(frame, frame_gray, cv.CV_RGB2GRAY)
        # We take the negative
        frame = cv.bitwise_not(frame)
        # We put a threshold
        ret, frame = cv.threshold(frame, threshold, 0, cv.THRESH_TOZERO)

        # place the window
        for ii, w in enumerate(windows_list):
            window_placement(frame, w.x, w.y, w.width, w.height,
                             (255, 0, 0), ii)

        # handle events
        k = cv.waitKeyEx(10)
        if k is str:
            k = ord(k)
        if k > 0:
            if k in STOP_INTERACTIVE:
                print('Starting analysis...')
                break
            elif k in MOVE_LEFT:
                x -= 1
            elif k in MOVE_UP:
                y -= 1
            elif k in MOVE_RIGHT:
                x += 1
            elif k in MOVE_DOWN:
                y += 1
            elif k in DECREASE_WINDOW:
                height -= 2
                width -= 2
            elif k in INCREASE_WINDOW:
                height += 2
                width += 2
            elif k in DECREASE_THRESHOLD:
                threshold -= 2
            elif k in INCREASE_THRESHOLD:
                threshold += 2
            elif k in SELECT_WINDOW:
                windows_list.append(window(x, y, width, height, threshold))
            elif k in REMOVE_WINDOW:
                if windows_list:
                    windows_list.pop()
            elif k in JUMP_TO_0:
                capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                print("Frame 0/%d" % (nb_frames))
            elif k in JUMP_TO_0_25:
                capture.set(cv.CAP_PROP_POS_FRAMES, int(nb_frames / 4))
                print("Frame %d/%d" % (int(nb_frames / 4), nb_frames))
            elif k in JUMP_TO_0_50:
                capture.set(cv.CAP_PROP_POS_FRAMES, int(nb_frames / 2))
                print("Frame %d/%d" % (int(nb_frames / 2), nb_frames))
            elif k in JUMP_TO_0_75:
                capture.set(cv.CAP_PROP_POS_FRAMES, int(3 * nb_frames / 4))
                print("Frame %d/%d" % (int(3 * nb_frames / 4), nb_frames))
            else:
                print(k)
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if (x + width) > cap_width:
            x = cap_width - width
        if (y + height) > cap_height:
            y = cap_height - height
        if threshold < 0:
            threshold = 0
        if threshold > 256:
            threshold = 256

        window_placement(frame, x, y, width, height, (0, 255, 0))
        # display image
        cv.imshow('Film', frame)

    cv.destroyWindow('Film')
    return windows_list, frame


def run_analysis(avifile, FPS, windowsfile=None):
    # create capture device
    print(avifile)
    capture = cv.VideoCapture(avifile)
    root, ext = os.path.splitext(avifile)
    root += time.strftime('_%Y-%m-%d_%Hh%M')
    config_file = root + '.txt'
    h5_file = root + '.h5'
    png_file = root + '.png'

    nb_frames = capture.get(cv.CAP_PROP_FRAME_COUNT)

    print("Frame rate : %g fps" % \
        capture.get(cv.CAP_PROP_FPS), FPS)

    print("Number of frames : %g" % nb_frames)
    # check if capture device is OK
    if not capture.isOpened():
        print("Error opening capture device")
        sys.exit(1)

    if windowsfile:
        windows_list = read_config(windowsfile)
        windows_list, frame = set_windows(capture, windows_list)
    else:
        windows_list, frame = set_windows(capture)
    save_config(windows_list, config_file)
    cv.imwrite(png_file, frame)
    capture.set(cv.CAP_PROP_POS_FRAMES, 0)

    data = get_IQ(capture, windows_list)
    out = tables.open_file(h5_file, 'w', title=avifile)
    out.create_array('/', 'IQ', data, title='Position of bacteria centre')
    out.create_array('/', 'FPS', FPS, title='Frames per second')
    table_windows = \
        out.create_table('/', 'windows', h5_window, 'Windows used in video')
    windows_to_h5(windows_list, table_windows)
    out.close()
    return h5_file

if __name__ == "__main__":
    avifile = sys.argv[1]
    fps = int(sys.argv[2])
    if len(sys.argv) > 3:
        windowsfile = sys.argv[3]
    else:
        windowsfile = None
    h5file = run_analysis(avifile, fps, windowsfile)
