#!/usr/bin/python3
# encoding: utf-8

'''MIT License

Copyright (c) [2016] [Scott Lawson]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

# Further development by ians.moyes@gmail.com

# Graphic user interface for audio responsive LED

# from __future__ import print_function
# from __future__ import division
import time
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
from pyqtgraph.dockarea import *

class GUI:
    plot = []
    curve = []

    def __init__(self, width=800, height=450, title=''):
        # Create GUI window
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title)
        self.win.resize(width, height)
        self.win.setWindowTitle(title)
        # Create GUI layout
        self.layout = QtGui.QVBoxLayout()
        self.win.setLayout(self.layout)

    def add_plot(self, title):
        new_plot = pg.PlotWidget()
        self.layout.addWidget(new_plot)
        self.plot.append(new_plot)
        self.curve.append([])

    def add_curve(self, plot_index, pen=(255, 255, 255)):
        self.curve[plot_index].append(self.plot[plot_index].plot(pen=pen))


if __name__ == '__main__':
    # Example test gui
    N = 48
    gui = GUI(title='Test')
    # Sin plot
    gui.add_plot(title='Sin Plot')
    gui.add_curve(plot_index=0)
    gui.win.nextRow()
    # Cos plot
    gui.add_plot(title='Cos Plot')
    gui.add_curve(plot_index=1)
    while True:
        t = time.time()
        x = np.linspace(t, 2 * np.pi + t, N)
        gui.curve[0][0].setData(x=x, y=np.sin(x))
        gui.curve[1][0].setData(x=x, y=np.cos(x))
        gui.app.processEvents()
        time.sleep(1.0 / 30.0)
