# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL,Qt
import logging
import TableView
from FileSize import format_size,File
logger = logging.getLogger("Model")

# TODO actually these models are different views on the data

# Common stuff
class TableModel(QtCore.QAbstractItemModel):
    def __init__(self, *args):
        apply(QtCore.QAbstractItemModel.__init__, (self, ) + args)
        self._root = None # start with empty tree
        self.idx_cache = {} # we must hold references to the indexes
        self.headers = ["File","Size"]
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            return QtCore.QVariant(self.headers[section])
        else:
            return QtCore.QVariant()
    def hasChildren(self, index):
        node = self.nodeFromIndex(index)
        if node is not None:
            return node.is_dir()
        else:
            return False
    def rowCount(self, parent):
        parent = self.nodeFromIndex(parent)
        if parent is not None and parent.is_dir():
            return len(parent.children)
        else:
            return 0
    def columnCount(self, parent):
        return 2
    def index(self, row, column, parent):
        parent = self.nodeFromIndex(parent)
        child = parent.children[row]
        idx = self.createIndex(row, column, child)
        self.idx_cache[id(child)] = idx
        return idx
    def parent(self, child_):
        child = self.nodeFromIndex(child_)
        if child is None:
            raise ValueError
        if child.parent is not None:
            # Do not create a new index here!
            try:
                return self.idx_cache[id(child.parent)]
            except KeyError:
                return QtCore.QModelIndex()
        else: # Parent of the root
            return QtCore.QModelIndex()
    def data(self, index, role):
        node = self.nodeFromIndex(index)
        # http://doc.trolltech.com/4.4/qt.html#ItemDataRole-enum
        if role == Qt.DecorationRole:
            return QtCore.QVariant()
        elif role == Qt.TextAlignmentRole:
            return QtCore.QVariant()
        elif role == Qt.DisplayRole:
            if index.column() == 0:
                return QtCore.QVariant(node.name)
            if index.column() == 1:
                return QtCore.QVariant(node.size)
        elif role == Qt.ToolTipRole:
            if index.column() == 0:
                p = [x.name for x in node.path]
                p = "/".join(p)
                return QtCore.QVariant(node.path_str)
            if index.column() == 1:
                return QtCore.QVariant(format_size(node.size))
        else:
            return QtCore.QVariant()
    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self._root
    def getRoot(self):
        return self._root
    def setRoot(self, root):
        self._root = root
        self.reset()
        self.idx_cache = {} # we must hold references to the indexes
    root = property(getRoot,setRoot)    

# Tree model
class SizeTableModel(TableModel):
    def __init__(self, *args):
        apply(TableModel.__init__, (self, ) + args)
    
# Flat table model
class FlatTableModel(TableModel):
    def __init__(self, *args):
        apply(TableModel.__init__, (self, ) + args)
        self.lst = [] # start with empty tree
    def rowCount(self, parent):
        return len(self.lst)
    def index(self, row, column, parent):
        child = self.lst[row]
        idx = self.createIndex(row, column, child)
        return idx
    def parent(self, child_):
        return QtCore.QModelIndex()
    def setRoot(self, root):
        TableModel.setRoot(self, root)
        if root is not None:
            self.lst = root.all_nondir_children()
        else:
            self.lst = []
        self.lst.sort(File.cmp)
        self.lst = self.lst[0:1000]
    root = property(TableModel.getRoot,setRoot)
