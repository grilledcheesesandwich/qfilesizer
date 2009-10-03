# -*- coding: utf-8 -*-
# TODO: - allow queue files for removal in interface (and remove them from the tree)
#       - show progress bar when loading directory
#       - allow changes to model
#         - manipulation/refresh
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL,Qt
import logging
import TableView
from FileSize import format_size,File
logger = logging.getLogger("MainWindow")

# QTableView http://qt.nokia.com/doc/4.5/qtableview.html
# We want to use an abstract table model
# Model is the File List (or at least, one level)
# example:
#   http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttablemodel/

# Abstrqct list model might be beter; we don't want per-cell selection
# is multi column list possible?  no, not anymore in Qt 4
# we need to use table
# 
# It seems QTreeView is actually the best, even though we do not intend to visualize a
# tree. Showing individual items without heirarchical structure is possible, and it 
# supports multiple rows.
# 

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
        self.lst = root.all_nondir_children()
        self.lst.sort(File.cmp)
        self.lst = self.lst[0:1000]
    root = property(TableModel.getRoot,setRoot)

class MainWindow(QtGui.QWidget):#MainWindow):
    def __init__(self, *args):
        #apply(QtGui.QMainWindow.__init__, (self, ) + args)
        apply(QtGui.QWidget.__init__, (self, ) + args)
        logger.info("Main window created")
        self.setWindowTitle("File size utility")
        self.vlayout = QtGui.QVBoxLayout(self)
        self.model = SizeTableModel()
        self.model2 = FlatTableModel()
        self.build_layout()

    def setData(self, data):
        self.model.root = data
        self.model2.root = data
    def getData(self):
        return self.model.root
    data = property(getData,setData)

    def build_layout(self):
        vlayout = self.vlayout

        tabwidget = QtGui.QTabWidget()
        vlayout.addWidget(tabwidget)

        # Tree view
        treeview = TableView.SizeTableView()
        treeview.setModel(self.model)
        treeview.afterModel()
        tabwidget.addTab(treeview, "Tree")

        # Flat view
        flatview = TableView.SizeTableView()
        flatview.setModel(self.model2)
        flatview.afterModel()
        tabwidget.addTab(flatview, "Flat")
        """
        button = QtGui.QPushButton("Reload view")
        self.connect(button, SIGNAL("clicked()"), self.reload)
        vlayout.addWidget(button)
        """

        button = QtGui.QPushButton("Load directory")
        self.connect(button, SIGNAL("clicked()"), self.load)
        vlayout.addWidget(button)

        button = QtGui.QPushButton("Quit")        
        self.connect(button, SIGNAL("clicked()"), self.close)
        vlayout.addWidget(button)

    def reload(self):
        logger.info("Reloading delegate and view")
        reload(TableView)
        
        # Remove the old
        while self.vlayout.takeAt(0) is not None:
            pass
        # Add the new
        self.build_layout()

    def load(self):
        dirname = QtGui.QFileDialog.getExistingDirectory (None, "Select a directory")
        logger.info("Load directory %s", dirname)
        dirname = str(dirname)
        from FileSize import recursive_walk
        rv = recursive_walk(dirname)
        rv.set_parents()
        self.data = rv
        logger.info("Finished -- models updated")

