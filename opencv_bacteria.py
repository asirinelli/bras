import sys
from opencv import cv, highgui
import numpy as np
import tables

class window:
    def __init__(self, x, y, width, height, threshold=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.threshold = threshold

def save_config(windows, name):
    out = file(name, 'w')
    for w in windows:
        out.write('%d\t%d\t%d\t%d\t%d\n' % (w.x, w.y, w.width, w.height, w.threshold))
    out.close()

def read_config(name):
    f = file(name, 'r')
    out = []
    for line in f:
        l = [int(ii) for ii in line.split()]
        out.append(window(*l))
    return out

def window_placement(image,x, y, width, height, color):
    cv.cvRectangle(image, cv.cvPoint(x, y),
                   cv.cvPoint(x + width, y + height),
                   color, 1, 8, 0)

def get_IQ(capture, windows):
  nb_frames = int(highgui.cvGetCaptureProperty(capture,
                                               highgui.CV_CAP_PROP_FRAME_COUNT))
#  data = [np.empty((nb_frames, 2))]*len(windows)
  data = np.empty((len(windows),nb_frames,2))
  crop_gray = []
  crop_rect = []
  matX = []
  matY = []
  for w in windows:
    crop_gray.append(cv.cvCreateMat(w.height, w.width, cv.CV_8UC1))
    crop_rect.append(cv.cvRect(w.x, w.y, w.width, w.height))
    mx, my = np.meshgrid(np.arange(w.width), np.arange(w.height))
    matX.append(mx)
    matY.append(my)
                     
  for fi in xrange(nb_frames):
    image = highgui.cvQueryFrame(capture)
    for ii in xrange(len(windows)):
      crop2 = crop_gray[ii]
      crop = cv.cvGetSubRect(image, crop_rect[ii])
      cv.cvCvtColor(crop, crop2, cv.CV_RGB2GRAY)
      cv.cvNot(crop2, crop2)
      cv.cvThreshold(crop2, crop2, windows[ii].threshold, 0,
                     cv.CV_THRESH_TOZERO)
      arr = np.array(crop2, dtype='int')#[:,:,0]

#      matX, matY = np.meshgrid(range(arr.shape[0]), 
#                               range(arr.shape[1]))

      M00 = np.sum(arr)
      M10 = np.sum(matX[ii]*arr)
      M01 = np.sum(matY[ii]*arr)
      X = float(M10)/float(M00)
      Y = float(M01)/float(M00)
#      data[ii][fi] = [X, Y]
      data[ii, fi] = np.array([X, Y])
    if fi%1000 == 0:
        print fi

#    print M00, norm, M10, M01, X, Y
#    cv.cvCircle(crop, cv.cvPoint(int(X), int(Y)),
#                2, cv.CV_RGB(0, 255, 0), -1, 8, 0)
#    print A, B, C, D, X, Y
  return data

def set_windows(capture, windows_list=[]):
    # create windows
    highgui.cvNamedWindow('Film', highgui.CV_WINDOW_AUTOSIZE)
    threshold = 128
    x = 200
    y = 100
    height = 20
    width = 20

    while 1:
        # capture the current frame
        frame = highgui.cvQueryFrame(capture)
        if frame is None:
            highgui.cvSetCaptureProperty(capture,
                                         highgui.CV_CAP_PROP_POS_FRAMES, 0)
            frame = highgui.cvQueryFrame(capture)

        # We take the negative
        cv.cvNot(frame, frame)
        # We put a threshold
        cv.cvThreshold(frame, frame, threshold, 0, cv.CV_THRESH_TOZERO)
 
        # place the window
        for w in windows_list:
            window_placement(frame, w.x, w.y, w.width, w.height,
                             cv.CV_RGB(255, 0, 0))
        window_placement(frame, x, y, width, height, cv.CV_RGB(0,255,0))
 
        # display image
        highgui.cvShowImage('Film', frame)
 
        # handle events
        k = highgui.cvWaitKey(10)
        if type(k) is str:
            if k == "q":
                print 'q pressed. Exiting ...'
                break
            elif ord(k) == 81:
                x -= 1
            elif ord(k) == 82:
                y -= 1
            elif ord(k) == 83:
                x += 1
            elif ord(k) == 84:
                y += 1
            elif ord(k) == 45:
                height -= 2
                width -= 2
            elif ord(k) == 43:
                height += 2
                width += 2
            elif ord(k) == 103:
              threshold -= 2
            elif ord(k) == 116:
              threshold += 2
            elif ord(k) == 32:
                windows_list.append(window(x, y, width, height, threshold))
            elif ord(k) == 8:
                if windows_list:
                    windows_list.pop()
#            else:
#              print ord(k)
    highgui.cvDestroyWindow('Film')
    return windows_list

                         
if __name__ == "__main__":
    print "OpenCV version: %d, %d, %d" % (cv.CV_MAJOR_VERSION,
                                               cv.CV_MINOR_VERSION,
                                               cv.CV_SUBMINOR_VERSION)
 
    print "Press q to exit ..."
 
 
    # create capture device
    capture = highgui.cvCreateFileCapture(sys.argv[1])
    nb_frames = highgui.cvGetCaptureProperty(capture,
                                             highgui.CV_CAP_PROP_FRAME_COUNT)
    print "Frame rate : %g fps"%highgui.cvGetCaptureProperty(capture,
                                                             highgui.CV_CAP_PROP_FPS)
    print "Number of frames : %g"%nb_frames

    # check if capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit(1)
    if len(sys.argv) > 2:
        windows_list = read_config(sys.argv[2])
        windows_list = set_windows(capture, windows_list)
    else:
        windows_list = set_windows(capture)
    save_config(windows_list, sys.argv[1][:-3]+'txt')
    highgui.cvSetCaptureProperty(capture, highgui.CV_CAP_PROP_POS_FRAMES, 0)

    data = get_IQ(capture, windows_list)
    out = tables.openFile(sys.argv[1][:-3]+'h5', 'w', title = sys.argv[1])
    out.createArray('/', 'IQ', data)
    out.close()
