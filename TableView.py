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
        if data<10000.0: # 10kB
            magnitude = 1
            MAX = 10000.0 
        elif data<1000000.0: # 1MB
            magnitude = 2
            MAX = 1000000.0
        elif data<100000000.0: # 100MB
            magnitude = 3
            MAX = 100000000.0
        else:  # 10GB
            magnitude = 4
            MAX = 10000000000.0 
        part = data/MAX
        # Draw bar
        (x,y,w,h) = option.rect.getRect()
        (x,y,w,h) = x+10,y+4,w-15,h-8
        #(x,y,w,h) = x+10,y+5,w-15,h-10
        #y -= (magnitude-1)
        #h += (magnitude-1)*2
        
        from math import ceil, log10
        wpart = ceil(w*part)
    
        # Background of bar
        #grad = GradientQT()
        #grad.setColorAt(0.0, QtGui.QColor(255,255,255))
        #grad.setColorAt(1.0, QtGui.QColor(128,128,128))
        #    Background color should be color(magnitude-1) ?
        #bar_bg_col = grad.getColorAt((magnitude-1)/4.0)
        bar_bg_col = QtGui.QColor(240,240,240)
        bar_bg = QtGui.QBrush(bar_bg_col)
        p.fillRect(x,y,w,h,bar_bg)

        # Set gradient based on magnitude
        grad = GradientQT()
        
        #grad.setColorAt(0.0, QtGui.QColor(220, 220, 220))
        #grad.setColorAt(0.5, QtGui.QColor(30, 255, 30))
        #grad.setColorAt(1.0, QtGui.QColor(30, 192, 30))
        grad.setColorAt(0.0, QtGui.QColor(200,200,255))
        grad.setColorAt(1.0, QtGui.QColor(60,60,255))
        

        # Color by logarithm
        import math
        base_col = grad.getColorAt((log10(data)-1.0) / 10.0)
        #base_col = grad.getColorAt((magnitude)/4.0)
        brush = QtGui.QBrush(base_col)
        p.fillRect(x,y,w*part,h, brush)

        # 3D ness
        # - caps at both sides
        brush = QtGui.QBrush(QtGui.QColor(0,0,0,100))
        p.fillRect(x,y,1,h, brush)
        p.fillRect(x+w-1,y,1,h, brush)
        # - slight left to right gradient
        brush = QtGui.QLinearGradient(x+1, y, x+w-1, y)  
        brush.setColorAt(0.0, QtGui.QColor(0,0,0,0))
        brush.setColorAt(1.0, QtGui.QColor(0,0,0,80))
        p.fillRect(x+1,y,w-2,h, brush)

        brush = QtGui.QLinearGradient(x, y, x, y+h)
        brush.setColorAt(0.0, QtGui.QColor(0,0,0,140)) # 128
        brush.setColorAt(0.5, QtGui.QColor(0,0,0,0))
        brush.setColorAt(1.0, QtGui.QColor(0,0,0,220)) # 200
        p.fillRect(x,y,w,h, brush)
        
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

        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.setMinimumSize(400,300)
    def afterModel(self):
        header = self.header()
        header.setStretchLastSection(False)

        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setResizeMode(1, QtGui.QHeaderView.Fixed)
        #header.setResizeMode(1, QtGui.QHeaderView.Interactive)
        header.resizeSection(1, 120)
        header.setMovable(False) # Don't allow moving header

        logger.info("Set up header")

#    def expanded(self): 
#       for column in range(self.model().columnCount(QModelIndex())):
#          self.resizeColumnToContents(column)        
