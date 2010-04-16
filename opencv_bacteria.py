import sys, os, time
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

class h5_window(tables.IsDescription):
    id = tables.UInt16Col()
    x = tables.UInt16Col()
    y = tables.UInt16Col()
    width = tables.UInt16Col()
    height = tables.UInt16Col()
    threshold = tables.UInt16Col()

def windows_to_h5(windows, table):
    row = table.row
    for ii,w in enumerate(windows):
        row['id'] = ii
        row['x'] = w.x
        row['y'] = w.y
        row['width'] = w.width
        row['height'] = w.height
        row['threshold'] = w.threshold
        row.append()

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

def window_placement(image,x, y, width, height, color, nb=None):
    cv.cvRectangle(image, cv.cvPoint(x, y),
                   cv.cvPoint(x + width, y + height),
                   color, 1, 8, 0)
    if nb != None:
        cv.cvPutText(image, '%0d'%nb, cv.cvPoint(x+width+2, y+height/2),
                     FONT, color)

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
    if windows_list:
        threshold = windows_list[-1].threshold
    else:
        threshold = 128
    x = 200
    y = 100
    height = 20
    width = 20
    cap_height = int(highgui.cvGetCaptureProperty(capture,
                                                  highgui.CV_CAP_PROP_FRAME_HEIGHT))
    cap_width = int(highgui.cvGetCaptureProperty(capture,
                                                 highgui.CV_CAP_PROP_FRAME_WIDTH))

#    frame_gray = cv.cvCreateMat(cap_height, cap_width, cv.CV_8UC1)
    while 1:
        # capture the current frame
        frame = highgui.cvQueryFrame(capture)
        if frame is None:
            highgui.cvSetCaptureProperty(capture,
                                         highgui.CV_CAP_PROP_POS_FRAMES, 0)
            frame = highgui.cvQueryFrame(capture)

        # cv.cvCvtColor(frame, frame_gray, cv.CV_RGB2GRAY)
        # We take the negative
        cv.cvNot(frame, frame)
        # We put a threshold
        cv.cvThreshold(frame, frame, threshold, 0, cv.CV_THRESH_TOZERO)
 
        # place the window
        for ii,w in enumerate(windows_list):
            window_placement(frame, w.x, w.y, w.width, w.height,
                             cv.CV_RGB(255, 0, 0), ii)
 
 
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
        window_placement(frame, x, y, width, height, cv.CV_RGB(0,255,0))
        # display image
        highgui.cvShowImage('Film', frame)

    highgui.cvDestroyWindow('Film')
    return windows_list, frame

                         
if __name__ == "__main__":
    print "OpenCV version: %d, %d, %d" % (cv.CV_MAJOR_VERSION,
                                               cv.CV_MINOR_VERSION,
                                               cv.CV_SUBMINOR_VERSION)
 
    print "Press q to exit ..."
 
 
    # create capture device
    capture = highgui.cvCreateFileCapture(sys.argv[1])
    root, ext = os.path.splitext(sys.argv[1])
    info_file = '/tmp/'+os.path.basename(root)+'.data'
    root += time.strftime('_%Y-%m-%d_%Hh%M')
    config_file = root + '.txt'
    h5_file = root + '.h5'
    png_file = root + '.png'

    FPS = int(sys.argv[2])

    nb_frames = highgui.cvGetCaptureProperty(capture,
                                             highgui.CV_CAP_PROP_FRAME_COUNT)
    print "Frame rate : %g fps"%highgui.cvGetCaptureProperty(capture,
                                                             highgui.CV_CAP_PROP_FPS), FPS
    print "Number of frames : %g"%nb_frames
    FONT = cv.cvInitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5)
    # check if capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit(1)

    if len(sys.argv) > 3:
        windows_list = read_config(sys.argv[3])
        windows_list, frame = set_windows(capture, windows_list)
    else:
        windows_list, frame = set_windows(capture)
    save_config(windows_list, config_file)
    highgui.cvSaveImage(png_file, frame)
    highgui.cvSetCaptureProperty(capture, highgui.CV_CAP_PROP_POS_FRAMES, 0)

    data = get_IQ(capture, windows_list)
    out = tables.openFile(h5_file, 'w', title = sys.argv[1])
    out.createArray('/', 'IQ', data, title='Position of bacteria centre')
    out.createArray('/', 'FPS', FPS, title='Frames per second')
    table_windows = out.createTable('/', 'windows', h5_window, 'Windows used in video')
    windows_to_h5(windows_list, table_windows)
    out.close()
    info = file(info_file, 'w')
    info.write(h5_file)
    info.close()
