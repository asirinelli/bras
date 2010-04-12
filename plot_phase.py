import pylab as P
import numpy as N
import sys, tables

FPS = int(sys.argv[1])

def smooth(x,window_len=11,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len<3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=N.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=N.ones(window_len,'d')
    else:
        w=eval('N.'+window+'(window_len)')

    y=N.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]

f = tables.openFile(sys.argv[2], 'r')
IQ = f.root.IQ.read()
for iq in IQ:
    P.figure()
    P.subplot(221)
    P.plot(iq[:,0],iq[:,1], ',')
    xc = iq[:,0] + 1j *iq[:,1]
    xc = xc -N.mean(xc)
    P.plot(xc.real, xc.imag, ',')
    P.axis('equal')
    P.grid()
    ph = N.unwrap(N.angle(xc))
    P.subplot(222)
    P.plot(ph)
    P.subplot(223)
    fact = FPS/2./N.pi
    P.plot(fact*N.diff(ph))
    P.plot(fact*smooth(N.diff(ph), FPS/10), lw=2)
    P.subplot(224)
    P.specgram(xc, NFFT=256, Fs=FPS, noverlap=255)
P.show()
