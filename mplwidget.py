#!/usr/bin/env python

# Python Qt4 bindings for GUI objects
from PyQt6 import QtWidgets

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# Matplotlib Figure object
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        #FigureCanvas.setSizePolicy(QtWidgets.QSizePolicy.expandingDirections,
        #                           QtWidgets.QSizePolicy.expandingDirections)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)


class MplWidget(QtWidgets.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtWidgets.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        # Declare the navigation bar
        self.navigation = NavigationToolbar(self.canvas, parent)
        # create a vertical box layout
        self.vbl = QtWidgets.QVBoxLayout()
        # add mpl widget to the vertical box
        self.vbl.addWidget(self.canvas)
        # add Navigation widget to vertical box
        self.vbl.addWidget(self.navigation)
        # set the layout to the vertical box
        self.setLayout(self.vbl)
