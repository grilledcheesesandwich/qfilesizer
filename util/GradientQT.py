# -*- coding: utf-8 -*-
import Gradient
from PyQt4.QtGui import QColor

class GradientQT(object):
    def __init__(self):
        self.inner = Gradient.Gradient()
    def getColorAt(self, pos):
        c = self.inner.get_color_at(pos)
        rv = QColor()
        rv.setRgbF(c[0], c[1], c[2], c[3])
        return rv
    def setColorAt(self, pos, color):
        c = (color.redF(), color.greenF(), color.blueF(), color.alphaF())
        self.inner.set_color_at(pos, c)
