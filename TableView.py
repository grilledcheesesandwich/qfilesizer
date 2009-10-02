# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL,Qt
import logging
from util.GradientQT import GradientQT

logger = logging.getLogger("TableView")

# How to show our own thing in the size column?
# Custom item delegate
# http://www.python-forum.org/pythonforum/viewtopic.php?f=4&t=14128
# QStyledItemDelegate
# http://qt.nokia.com/doc/4.5/qstyleditemdelegate.html
# QStyledItemDelegate::paint ( QPainter * painter, const QStyleOptionViewItem & option, const QModelIndex & index ) const 
# When displaying data from models in Qt item views, e.g., a QTableView, the individual items are drawn by a delegate. 
#        view.setItemDelegate(delegate); 
#             setItemDelegateForColumn <- exactly what we need
# change render based on 'option' or 'index'

# http://qt.nokia.com/doc/4.5/qt.html#ItemDataRole-enum
# Qt.UserRole
# (*iter)->data(1,Qt::UserRole).value();    user data for model
#    data can also be applied to a QModelIndex
class ItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, *args):
        apply(QtGui.QStyledItemDelegate.__init__, (self, ) + args)
    def paint(self, p, option, index):
        data = index.data(Qt.DisplayRole)
        data = data.toLongLong()[0]
        p.save()
        p.setClipRect(option.rect)
        # Draw background according to current style
        style = QtGui.QApplication.style()
        style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem, option, p) # ,widget
        # Process data
        if data<1000.0:
            magnitude = 1
            MAX = 1000.0
        elif data<1000000.0:
            magnitude = 2
            MAX = 1000000.0
        elif data<1000000000.0:
            magnitude = 3
            MAX = 1000000000.0 # 1Gb
        else: #if data<1000000000.0:
            magnitude = 4
            MAX = 1000000000000.0 # 1000Gb
        part = data/MAX
        # Draw bar
        (x,y,w,h) = option.rect.getRect()
        (x,y,w,h) = x+10,y+4,w-20,h-8
    
        # Background of bar
        bar_bg = QtGui.QBrush(QtGui.QColor(240,240,240))
        p.fillRect(x,y,w,h,bar_bg)

        # Set gradient based on magnitude
        grad = GradientQT()
        grad.setColorAt(0.0, QtGui.QColor(220, 220, 220))
        #grad.setColorAt(1.0, QtGui.QColor(30, 30, 255))
        grad.setColorAt(1.0, QtGui.QColor(30, 255, 30))
        # Color by logarithm
        import math
        base_col = grad.getColorAt((math.log10(data)-1.0) / 10.0)
        brush = QtGui.QBrush(base_col)
        p.fillRect(x,y,w*part,h, brush)

        brush = QtGui.QLinearGradient(x, y, x+w, y)
        brush.setColorAt(0.0, QtGui.QColor(0,0,0,128))
        brush.setColorAt(0.1, QtGui.QColor(0,0,0,0))
        brush.setColorAt(0.9, QtGui.QColor(0,0,0,0))
        brush.setColorAt(1.0, QtGui.QColor(0,0,0,128))
        p.fillRect(x,y,w*part,h, brush)

        brush = QtGui.QLinearGradient(x, y, x, y+h)
        brush.setColorAt(0.0, QtGui.QColor(0,0,0,128))
        brush.setColorAt(0.5, QtGui.QColor(0,0,0,0))
        brush.setColorAt(1.0, QtGui.QColor(0,0,0,200))
        p.fillRect(x,y,w*part,h, brush)
        
        # Boxes that signify magnitude
        brush = QtGui.QLinearGradient(x, y, x, y+h)
        brush.setColorAt(0.0, QtGui.QColor(255,255,0))
        brush.setColorAt(0.5, QtGui.QColor(255,0,0))
        brush.setColorAt(1.0, QtGui.QColor(0,0,0))
        (x,y,w,h) = option.rect.getRect()
        for xx in xrange(0, magnitude-1):
            if xx < (magnitude-1):
                b = brush
            else:
                b = bar_bg
            p.fillRect(x+4,y+h-((xx+1)*4)-4, 5, 3, b)
        """
        # new old idea
        # vertical gradient based on magnitude
        # horizontal fill based on size within magnitude
        # vertical "stars" before bar will signify magnitude as well
        # or marker bar
        # fire color scheme
        # "fast reload view" button for quick prototyping
        # scale/zoom/animate, so that relationships can be seen
        # keep color scheme the same, so that it scales with the values?

        #if data<1000.0:
        #    magnitude = 1
        #    MAX = 1000.0
        #elif data<1000000.0:
        #    magnitude = 2
        #    MAX = 1000000.0
        #else: #if data<1000000000.0:
        #    magnitude = 3
        #    MAX = 1000000000.0 # 1Gb

        #print data, option.rect, int(option.state)
        # Draw bar
        # Height depend on size magnitude (gb,mb,kb,..)
        (x,y,w,h) = option.rect.getRect()
        (x,y,w,h) = x+5,y+4,w-10,h-8
        #part = min(data/MAX, 1.0) / 3.0
        #part += (magnitude-1)/3.0
        #import math
        #part = (math.log10(data)-1.0)/10.0
        #part = data / 1000000000.0
        #magnitude = 1
        #if part > 1.0:
        #    magnitude = 2
        #if part > 2.0:
        #    magnitude = 3
        #part /= magnitude
        #if part<0.0:
        #    part = 0.0
        #if part>1.0:
        #    part = 1.0
        blocks = 40
        base_size = 1000
        val1 = (data/base_size)%blocks
        val2 = (data/(base_size*blocks))%blocks
        val3 = (data/(base_size*blocks*blocks))
        block_width = 5
        block_height = 3
        block_xsep = 6

        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(96.0,96.0,255.0))
        brush.setColorAt(1.0, QtGui.QColor(96.0,96.0,255.0))

        for xx in xrange(0, val1):
            p.fillRect(x + xx*block_xsep, y, block_width, block_height, brush)

        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(0.0,0.0, 96.0))
        brush.setColorAt(1.0, QtGui.QColor(0.0,0.0,96.0))

        for xx in xrange(0, val2):
            p.fillRect(x + xx*block_xsep, y+4, block_width, block_height, brush)

        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(0.0,0.0, 0.0))
        brush.setColorAt(1.0, QtGui.QColor(0.0,0.0, 0.0))

        for xx in xrange(0, val3):
            p.fillRect(x + xx*block_xsep, y+8, block_width, block_height, brush)

        """
        """
        p.setClipRect(QtCore.QRect(x, y, w*val1, h))
        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(192.0,192.0, 192.0))
        brush.setColorAt(1.0, QtGui.QColor(96.0,96.0,255.0))
        p.fillRect(x, y, w, 3, brush)

        p.setClipRect(QtCore.QRect(x, y, w*val2, h))
        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(96.0,96.0, 96.0))
        brush.setColorAt(1.0, QtGui.QColor(0.0,0.0,96.0))
        p.fillRect(x, y+4, w, 3, brush)

        p.setClipRect(QtCore.QRect(x, y, w*val3, h))
        brush = QtGui.QLinearGradient(x, y, x+w, y+h)
        brush.setColorAt(0.0, QtGui.QColor(96.0,96.0, 96.0))
        brush.setColorAt(1.0, QtGui.QColor(255.0,0.0, 0.0))
        p.fillRect(x, y+8, w, 3, brush)
        """
        

        
        
        p.restore()
        # QtGui.QStyle.State_MouseOver
        # QtGui.QStyle.State_Selected
        # QtGui.QStyle.State_HasFocus
        # XXX render data using painter in option.rect
        # set background color etc based on default for state
        #   http://qt.nokia.com/doc/4.5/qstyle.html
        #   QStyleOptionFocusRect option;
        #   option.initFrom(this);
        #   option.backgroundColor = palette().color(QPalette::Background);
        #   style()->drawPrimitive(QStyle::PE_FrameFocusRect, &option, &painter, this);

        # src/gui/itemviews/qstyleditemdelegate.cpp
        # src/gui/styles/qcommonstyle.cpp

        #QtGui.QStyledItemDelegate.paint(self, painter, option, index)

        # Draw a bar
        # If files too big make /  / in bar (as in continues here)
        # Scale everything accordingly
"""
    QStyleOptionViewItemV4 opt = option;
    initStyleOption(&opt, index);

    const QWidget *widget = QStyledItemDelegatePrivate::widget(option);
    QStyle *style = widget ? widget->style() : QApplication::style();
    style->drawControl(QStyle::CE_ItemViewItem, &opt, painter, widget);

p->save();
p->setClipRect(opt->rect);
... drawPrimitive(PE_PanelItemViewItem, opt, p, widget);
draw focus rectangle
opt->state & QStyle::State_HasFocus
drawPrimitive(QStyle::PE_FrameFocusRect, &o, p, widget);
p->restore();


"""

class SizeTableView(QtGui.QTreeView):
    def __init__(self, *args):
        apply(QtGui.QTreeView.__init__, (self, ) + args)

        self.delegate = ItemDelegate()
        self.setItemDelegateForColumn(1, self.delegate)

        self.setMinimumSize(400,300)
    def afterModel(self):
        header = self.header()
        header.setStretchLastSection(False)

        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setResizeMode(1, QtGui.QHeaderView.Fixed)
        #header.setResizeMode(1, QtGui.QHeaderView.Interactive)
        header.resizeSection(1, 160)
        header.setMovable(False) # Don't allow moving header

        logger.info("Set up header")

#    def expanded(self): 
#       for column in range(self.model().columnCount(QModelIndex())):
#          self.resizeColumnToContents(column)        
