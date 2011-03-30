===============
 Documentation
===============

BRAS
====

This aim of this program is to extract from a video the movement of
bacteria. It can analyse an almost unlimited number of bacteria and
its speed is determined by the data transfer rate.

The user sets up interactively windows of interest to be
analysed. Each window contains a single cell and a luminosity
threshold is associated to remove the background information. The
program calculates for each windows the position of the bacterium
centre of mass along the time.

Inputs
------

The program takes as input a video file. Depending of the OpenCV
version used, you may need to use uncompress video format. You can
also provide a configuration file. Each time you analyse a video, a
configuration file is saved containing the windows positions and
intensity thresholds. If an experiment is split in multiple video
files, you can use this file to keep the same windows across the
experiment videos.

As some video recorders may not record the frame per second (FPS)
rate, it has to be set manually to avoid any errors in the later speed
measurement.

Utilisation
-----------

A window showing the movie to be analysed is first opened. Using the
keyboard, regions of interest have to be set. The following keys are
available:

* **+**/**-**: change the window size
* **[left]**/**[right]**/**[up]**/**[down]**: move the window
* **[space]**: select current window for analysis
* **[backspace]**: remove previously selected window
* **g**/**t**: change the contrast threshold
* **z**, **x**, **c**, **v**: jump to start, 25%, 50%, 75%
* **q**: launch the analysis

The active window is in green while the already selected ones are in
red. You can move the active window using the arrow keys and change
its size. One important parameter is the contrast threshold: it is
used to isolate the bacteria from the video background. When correctly
set, you should see cleary the the bacteria in grey/white while the
background should be black. When the position, the size and the
contrast of the active window are set, you can store this setting with
the space bar and select another bacteria.

You can start the analysis of the movie by pressing the 'q' key. A
monitor window will then appear to track the analysis process. At the
end, graphs will be plotted showing the analysis done. They show the
displacement of the bacteria in the window reference, the number of
turns done function of the time and a simple analysis of the rotation
speed.

Outputs
-------

*BRAS* saves at the end of the analysis, 3 kind of files in the video
directory:

* An **HDF5** file (suffix: *.h5*) containing all the data. 3 datasets
  are stored in this file:

  * ``FPS``: the frame per second parameter
  * ``windows``: structure containing the region of interest
    (position, size, contrast threshold, number)
  * ``IQ``: 3D array containing the positions (x,y) positions for each
    bacteria for each frame.

* A **video frame image** with the region of interest and their index
  overlayed.
* The first analysis **plots** displayed at the end of the processing.

**HDF5** files can be opened by most of the data processing softwares
or languages: Python (using `PyTables`_ or `h5py`_), `R`_, `Octave`_,
`Matlab`_, IDL, LabView, `Mathematica`_... This file is used by *Click
& Mean* for the subsequent analysis.

Click & Mean
============



Video Player
============

This is a simple video analyser. You can move easily along your movie
with a slider or move frame by frame using the side buttons. It gives
you the position in minutes and seconds or in frame number. When
opening a video, you can as an option open the *HDF5* file associated
to the movie. If you decide to do so, you will be able to visualise
the regions of interest and their number.

You can also export the displayed frame as a *PNG* picture.


.. _`PyTables`: http://www.pytables.org/
.. _`h5py`: http://h5py.alfven.org/
.. _`Matlab`: http://www.mathworks.com/help/techdoc/ref/hdf5.html
.. _`Mathematica`: http://reference.wolfram.com/mathematica/ref/format/HDF5.html
.. _`Octave`: http://www.gnu.org/software/octave/doc/interpreter/Simple-File-I_002fO.html
.. _`R`: http://lib.stat.cmu.edu/R/CRAN/web/packages/hdf5/index.html

..
   Local Variables:
   mode: rst
   mode: ispell-minor
   ispell-dictionary: "british"
   End:
