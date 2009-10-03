#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import logging
from MainWindow import MainWindow

# ==== Basic initialisation ====

# Logging
logging.basicConfig(level=logging.DEBUG,
            datefmt='%a, %d %b %Y %H:%M:%S',
            format='%(asctime)s %(levelname)-8s %(name)-8s %(message)s',
            stream=sys.stdout)

# Load data (debug)
rv = None
if len(sys.argv)==2 and sys.argv[1]=="-d":
    import pickle
    f = open("sizes.pickle", "rb")
    rv = pickle.load(f)
    f.close()
    rv.set_parents()

# Qt Application
app = QtGui.QApplication(sys.argv)
dt = MainWindow()
dt.data = rv
dt.show()
app.exec_()

