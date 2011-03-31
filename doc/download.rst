==============
 Installation
==============

The software development is hosted on `Sourceforge`_. You can access
to all the sources and binaries by visiting the `BRAS Project Homepage`_


Windows binary installer
========================

A Windows package is available. It includes all the libraries
needed. You can download and install it: `BRAS_installer_v1.0.exe
<http://sourceforge.net/projects/bras/files/BRAS%201.0/BRAS_installer_v1.0.exe/download>`_

Once installed, you will find all the tools in your usual Windows
application menu.

Using the Python sources
========================

For Linux or MacOS, there is no binary distribution yet available. You
need to have all the libraries required installed beforehand.

Prerequisite
------------

This set of programs, written in `Python <http://www.python.org>`_,
needs the following programs or libraries:

* **Python**: `Download Python <http://www.python.org/download/>`_
* **PyQt4** is a python wrapper to the Qt toolkit used to generate the
  GUI: `Download PyQt4
  <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_
* **OpenCV** is Computer Vision library used to extract and manipulate
  frames from the videos: `Download OpenCV
  <http://opencv.willowgarage.com/wiki/>`_ *(Please use version 2.1)*
* **NumPy** is an array manipulation library: `Download NumPy
  <http://www.scipy.org/Download>`_
* **SciPy** is a scientific library: `Download Scipy
  <http://www.scipy.org/Download>`_
* **matplotlib** is a 2D plotting library: `Download matplotlib
  <http://matplotlib.sourceforge.net/>`_
* **PyTables** is a library to manage dataset using HDF5: `Download
  PyTables <http://www.pytables.org/moin/Downloads>`_

Most of the linux distributions provide these packages. Please read
your distribution documentation to find out how to install them. On a
Debian linux system, the following command will do the work::

  apt-get install python-qt4 python-opencv python-numpy python-scipy python-matplotlib python-tables

The required packages and all their dependencies will automatically
downloaded and installed.

On Windows, one can use the scientific python distribution
`Python(x,y) <http://www.pythonxy.com/>`_ which already includes all
the needed packages (except OpenCV).

Download BRAS
-------------

The program sources can be downloaded on the `BRAS Project Files
section <http://sourceforge.net/projects/bras/files/>`_.

You can also download the development version using `git`_. Please
follow the instruction available `here
<http://sourceforge.net/scm/?type=git&group_id=518962>`_.

Running BRAS
------------

Once you have extracted the archive, you will be able to run the 3
programs provided: **BRAS** (``launch_analysis.py``), **Click & Mean**
(``click_mean2.py``) and **Video Player** (``video.py``).

.. _`Sourceforge`: http://sourceforge.net/
.. _`BRAS Project Homepage`: http://sourceforge.net/projects/bras/
.. _`git`: http://git-scm.com/
..
   Local Variables:
   mode: rst
   mode: auto-fill
   mode: ispell-minor
   ispell-dictionary: "british"
   End:
