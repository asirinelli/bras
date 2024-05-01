#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simply display the analysis done on a movie.
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

import matplotlib
matplotlib.use('QtAgg')
import pylab as P
import numpy as N
import sys
import tables
import os
P.ioff()


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

    s = N.r_[2 * x[0] - x[window_len:1:-1],
             x,
             2 * x[-1] - x[-1:-window_len:-1]]

    if window == 'flat':  # moving average
        w = N.ones(window_len, 'd')
    else:
        w = eval('N.' + window + '(window_len)')

    y = N.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


def plot_phase(h5file):
    f = tables.open_file(h5file, 'r')
    IQ = f.root.IQ.read()
    FPS = f.root.FPS.read()
    f.close()
    ii = 0
    for iq in IQ:
        fig = P.figure()
        fig.suptitle(os.path.split(h5file)[1] + " # %d" % ii)
        ax1 = P.subplot(221)
        P.plot(iq[:, 0], iq[:, 1], ',')
        xc = iq[:, 0] + 1j * iq[:, 1]
        xc = xc - N.mean(xc)
        P.plot(xc.real, xc.imag, ',')
        P.axis('equal')
        P.grid()
        ph = N.unwrap(N.angle(xc))
        time = N.arange(len(ph), dtype=float) / FPS

        ax2 = P.subplot(222)
        ax2.yaxis.set_label_position('right')
        ax2.yaxis.set_ticks_position('right')
        P.plot(time, ph / 2. / N.pi)
        P.ylabel('Turns')
        P.grid()
        ax3 = P.subplot(223, sharex=ax2)
        fact = FPS / 2. / N.pi
        P.plot(time[:-1], fact * N.diff(ph))
        P.plot(time[:-1], fact * smooth(N.diff(ph), int(FPS / 10)), lw=2)
        P.grid()
        P.xlabel('time (s)')
        P.ylabel('Rotation per second')

        ax4 = P.subplot(224, sharex=ax3, sharey=ax3)
        ax4.yaxis.set_label_position('right')
        ax4.yaxis.set_ticks_position('right')
        P.specgram(xc, NFFT=256, Fs=FPS, noverlap=0)
        P.grid()
        P.xlabel('time (s)')
        P.ylabel('Rotation per second')
        P.savefig(os.path.splitext(h5file)[0] + "_%02d.png" % ii)
        ii += 1
    P.show()

if __name__ == "__main__":
    plot_phase(sys.argv[1])
