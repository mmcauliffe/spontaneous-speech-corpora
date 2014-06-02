import math
from linghelper.phonetics.representations.amplitude_envelopes import to_envelopes
from linghelper.phonetics.representations.prosody import to_pitch,to_intensity,to_prosody
from linghelper.phonetics.representations.mfcc import to_mfcc
from linghelper.phonetics.representations.mhec import to_mhec
from linghelper.distance.dtw import dtw_distance
from linghelper.distance.dct import dct_distance
from linghelper.distance.xcorr import xcorr_distance


import os
import networkx as nx
import numpy
import scipy.signal

from PySide.QtCore import (qAbs, QLineF, QPointF, qrand, QRectF, QSizeF, qsrand,
        Qt, QTime,QSettings,QSize,QPoint,QAbstractTableModel)
from PySide.QtGui import (QBrush, QKeySequence, QColor, QLinearGradient, QPainter,
        QPainterPath, QPen, QPolygonF, QRadialGradient, QApplication, QGraphicsItem, QGraphicsScene,
        QGraphicsView, QStyle,QMainWindow, QAction, QDialog, QDockWidget,
        QFileDialog, QListWidget, QMessageBox,QTableWidget,QTableWidgetItem,QDialog)

from db_models import Speaker,Dialog, WordToken

class SpeakerTable(QAbstractTableModel):
    def __init__(self,parent=None):
        super(SpeakerTable, self).__init__(parent=parent)
        self.query = None
        self.columns = [x.key for x in Speaker.__table__.columns if x.key != 'id']

    def setQuery(self,query):
        self.query = query

    def rowCount(self,parent=None):
        if self.query is None:
            return 0
        return len(self.query)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        s = self.query[row]
        data = getattr(s,self.columns[col])
        return data

class DialogTable(QAbstractTableModel):
    def __init__(self,parent=None,query=None):
        super(DialogTable, self).__init__(parent=parent)
        self.query = query
        self.columns = [x.key for x in Dialog.__table__.columns if x.key != 'id']

    def setQuery(self,query):
        self.query = query

    def rowCount(self,parent=None):
        if self.query is None:
            return 0
        return len(self.query)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        s = self.query[row]
        data = getattr(s,self.columns[col])
        return data

class WordTokenTable(QAbstractTableModel):
    def __init__(self,parent=None,query=None):
        super(WordTokenTable, self).__init__(parent=parent)
        self.query = query
        self.columns = [x.key for x in WordToken.__table__.columns if x.key != 'id']

    def setQuery(self,query):
        self.query = query

    def rowCount(self,parent=None):
        if self.query is None:
            return 0
        return len(self.query)

    def columnCount(self,parent=None):
        return len(self.columns)

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        s = self.query[row]
        data = getattr(s,self.columns[col])
        return data



