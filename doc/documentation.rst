===============
 Documentation
===============

OpenCV Bacteria
===============

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

Utilisation
-----------

Outputs
-------

Click & Mean
============


..
   Local Variables:
   mode: rst
   mode: ispell-minor
   ispell-dictionary: "british"
   End:
