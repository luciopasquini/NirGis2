# -*- coding: utf-8 -*-
from qgis.core import *
try:
    __QGis_version__ = 3
    Qgis.QGIS_VERSION_INT
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,Qt,pyqtSignal
    from PyQt5.QtGui import QIcon,QKeySequence,QCursor
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class squareMapTool(QgsMapTool):

    def __init__(self, canvas,button):
        QgsMapTool.__init__(self,canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.button = button

    def canvasMoveEvent(self,event):
        self.movedMo.emit({'x': event.pos().x(), 'y': event.pos().y()})

    def canvasReleaseEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit({'x': event.pos().x(), 'y': event.pos().y()})

    def activate(self):
        QgsMapTool.activate(self)
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.deactivateLine.emit()
        QgsMapTool.deactivate(self)

    def isZoomTool(self):
        return False

    def setCursor(self,cursor):
        self.cursor = QCursor(cursor)
    movedMo = pyqtSignal(dict)
    leftClicked = pyqtSignal(dict)
    deactivateLine = pyqtSignal()
