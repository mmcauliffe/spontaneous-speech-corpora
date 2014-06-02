
import math


import os
import numpy
import csv

from PySide.QtCore import (qAbs, QLineF, QPointF, qrand, QRectF, QSizeF, qsrand,
        Qt, QTime,QSettings,QSize,QPoint)
from PySide.QtGui import (QBrush, QKeySequence, QColor, QLinearGradient, QPainter,
        QPainterPath, QPen, QPolygonF, QRadialGradient, QApplication, QGraphicsItem, QGraphicsScene,
        QGraphicsView, QStyle,QMainWindow, QAction, QDialog, QDockWidget,
        QFileDialog, QListWidget, QMessageBox,QTableWidget,QTableWidgetItem,QDialog,
        QTableView,QAbstractItemView, QMenu)


class TableWidget(QTableView):
    def __init__(self,parent=None):
        super(TableWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)
        
    def popup(self,pos):
        print(self.model().data(self.indexAt(pos)))
        print(self.indexAt(pos))
        print(self.indexAt(pos).row())
        menu = QMenu()
        
        saveRepAction = QAction(self)
        saveRepAction.setText('Save representation...')
        saveRepAction.triggered.connect(lambda: self.saveRep(self.indexAt(pos)))
        menu.addAction(saveRepAction)
        action = menu.exec_(self.mapToGlobal(pos))
    
    def saveRep(self,index):
        print(index)
        gInd = index.row()
        name = self.model().data(index)
        filename,filt = QFileDialog.getSaveFileName(self,"Save representation",os.path.join(os.getcwd(),name.replace('.wav','.txt')),"Text files (*.txt)")
        
        rep = self.model().rep
        for n in self.model().g.nodes_iter(data=True):
            if n[0] == gInd:
                rep = n[1]['acoustics'][rep]
                break
        
        time_step = self.model().time_step
        num_frames,num_bands = rep.shape
        with open(filename,'w') as f:
            writer = csv.writer(f,delimiter='\t')
            writer.writerow(['Time','Band','Amplitude'])
            for i in range(num_frames):
                for j in range(num_bands):
                    writer.writerow([(i+1)*time_step,j+1,rep[i,j]])
        #if dialog.exec_():
        #    fileNames = dialog.selectedFiles()
