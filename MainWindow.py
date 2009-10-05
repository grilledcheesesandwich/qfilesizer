# -*- coding: utf-8 -*-
# TODO: - allow queue files for removal in interface (and remove them from the tree)
#       - show progress bar when loading directory
#       - allow changes to model
#         - manipulation/refresh
#       - split MainWindow file into individual classes
#       - selection should be synced between both models
#         - handle selection in base structure, then send signals when it changed
#  deletion:
#       - show statistics about selected files (number of files + total size)
#           http://doc.trolltech.com/4.4/qitemselectionmodel.html#selectedIndexes
#           QItemSelectionModel
#           QItemSelectionModel * QAbstractItemView::selectionModel () const
#           signal: void selectionChanged ( const QItemSelection & selected, const QItemSelection & deselected )
#       - allow dumping list of selected files to text file

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import SIGNAL,Qt
import logging
import TableView
from FileSize import format_size,File
from Models import SizeTableModel,FlatTableModel

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

        hlayout = QtGui.QHBoxLayout()
        vlayout.addLayout(hlayout)

        tabwidget = QtGui.QTabWidget()
        hlayout.addWidget(tabwidget)

        # Tree view
        treeview = TableView.SizeTableView()
        treeview.setModel(self.model)
        treeview.afterModel()
        tabwidget.addTab(treeview, "Tree")

        # Flat view
        flatview = TableView.SizeTableView()
        flatview.setModel(self.model2)
        flatview.afterModel()
        # doesn't work, because model is subtly different
        # flatview.setSelectionModel(treeview.selectionModel())
        self.selmod1 = treeview.selectionModel()
        self.connect(self.selmod1, SIGNAL("selectionChanged(const QItemSelection &, const QItemSelection &)"), self.selectionChanged)

        tabwidget.addTab(flatview, "Flat")

        buttonbar = QtGui.QHBoxLayout()
        vlayout.addLayout(buttonbar)
        
        #button = QtGui.QPushButton("Reload view")
        #self.connect(button, SIGNAL("clicked()"), self.reload)
        #buttonbar.addWidget(button)

        button = QtGui.QPushButton("Load directory")
        self.connect(button, SIGNAL("clicked()"), self.load)
        buttonbar.addWidget(button)

        button = QtGui.QPushButton("Quit")        
        self.connect(button, SIGNAL("clicked()"), self.close)
        buttonbar.addWidget(button)

        # Statistics
        grid = QtGui.QVBoxLayout()
        hlayout.addLayout(grid)
        grid.addWidget(QtGui.QLabel("Total size:"))
        self.stats1 = QtGui.QLabel("0")
        grid.addWidget(self.stats1)
        grid.addWidget(QtGui.QLabel("Files selected:"))
        self.stats2 = QtGui.QLabel("0")
        grid.addWidget(self.stats2)
        grid.addStretch(1)

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
        if not dirname:
            return # Nothing selected
        logger.info("Load directory %s", dirname)
        dirname = str(dirname)
        from FileSize import recursive_walk
        rv = recursive_walk(dirname)
        rv.set_parents()
        self.data = rv
        logger.info("Finished -- models updated")

    def selectionChanged(self, selected, deselected):
        """Selection changed -- update stats"""
        rows = [self.model.nodeFromIndex(row) for row in self.selmod1.selectedRows()]
        self.updateStats(rows)

    def updateStats(self, rows):
        self.stats1.setText(format_size(sum([x.size for x in rows])))
        self.stats2.setText(str(len(rows)))
        
