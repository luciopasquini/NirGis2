# -*- coding: utf-8 -*-
"""
/***************************************************************************
 lineFreeHand
                                 A QGIS plugin
 Calcolo della sezione  di  campo orizzontale
                             -------------------
        begin                : 2014-08-16
        copyright            : (C) 2014 by arpav
        email                : lpasquini@arpa.veneto.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import *
try:
    __QGis_version__ = 3
    Qgis.QGIS_VERSION_INT
    from PyQt5.QtCore import QSettings,Qt,QObject
    from PyQt5.QtGui import QIcon,QKeySequence,QCursor,QColor
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
from squareMapTool import squareMapTool
import pdb
class squareFreeHand(QObject):
    def __init__(self,iface,actFreeHandSez):
        QObject.__init__(self)
        self.iface = iface
        self.actFreeHandSez = actFreeHandSez
        self.canvas = self.iface.mapCanvas()
        self.lineTool = squareMapTool(self.canvas,self.actFreeHandSez)
        if __QGis_version__ == 3:
            self.lineRubberBand = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
        else:
            self.lineRubberBand = QgsRubberBand(self.iface.mapCanvas(), QGis.Line)
        self.lineRubberBand.setWidth(2)
        self.lineRubberBand.setColor(QColor(Qt.red))
        self.lineRubberBand.setLineStyle(Qt.DashLine)
        self.drowLine = False
        self.startX = 0
        self.startY = 0
        self.laySez = None

    def startSquareDraw(self,laySez):
        self.saveTool = self.canvas.mapTool()
        self.connectTool()
        self.canvas.setMapTool(self.lineTool)
        self.laySez = laySez

    def connectTool(self):
        self.lineTool.movedMo.connect(self.moved)
        self.lineTool.leftClicked.connect(self.leftClicked)
        self.lineTool.deactivateLine.connect(self.deactivate)

    def deactivate(self):
        self.drowLine = False
        self.lineTool.deactivateLine.disconnect(self.deactivate)
        self.lineTool.leftClicked.disconnect(self.leftClicked)
        self.lineTool.movedMo.disconnect(self.moved)
        if __QGis_version__ == 3:
            self.lineRubberBand.reset(QgsWkbTypes.LineGeometry)
        else:
            self.lineRubberBand.reset(QGis.Line)


    def moved(self,position):
        if self.drowLine :
            myPosiz = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            if __QGis_version__ == 3:
                self.lineRubberBand.reset(QgsWkbTypes.LineGeometry)
                self.lineRubberBand.addPoint(QgsPointXY(self.startX,self.startY))
                self.lineRubberBand.addPoint(QgsPointXY(self.startX,myPosiz.y()))
                self.lineRubberBand.addPoint(QgsPointXY(myPosiz.x(),myPosiz.y()))
                self.lineRubberBand.addPoint(QgsPointXY(myPosiz.x(),self.startY))
                self.lineRubberBand.addPoint(QgsPointXY(self.startX,self.startY))
            else:
                self.lineRubberBand.reset(QGis.Line)
                self.lineRubberBand.addPoint(QgsPoint(self.startX,self.startY))
                self.lineRubberBand.addPoint(QgsPoint(self.startX,myPosiz.y()))
                self.lineRubberBand.addPoint(QgsPoint(myPosiz.x(),myPosiz.y()))
                self.lineRubberBand.addPoint(QgsPoint(myPosiz.x(),self.startY))
                self.lineRubberBand.addPoint(QgsPoint(self.startX,self.startY))
    def leftClicked(self,position):
        if self.drowLine :
            myPosiz = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            self.drowLine = False
            self.canvas.unsetMapTool(self.lineTool)
            self.canvas.setMapTool(self.saveTool)
            if __QGis_version__ == 3:
                self.lineRubberBand.reset(QgsWkbTypes.LineGeometry)
            else:
                self.lineRubberBand.reset(QGis.Line)
            if self.laySez :
                pr = self.laySez.dataProvider()
                if __QGis_version__ == 3:
                    geomSquare = QgsGeometry.fromPolygonXY([[QgsPointXY(self.startX,self.startY),
                                                       QgsPointXY(self.startX,myPosiz.y()),
                                                       QgsPointXY(myPosiz.x(),myPosiz.y()),
                                                       QgsPointXY(myPosiz.x(),self.startY)]])
                    print (geomSquare)
                else:
                    geomSquare = QgsGeometry.fromPolygon([[QgsPoint(self.startX,self.startY),
                                                       QgsPoint(self.startX,myPosiz.y()),
                                                       QgsPoint(myPosiz.x(),myPosiz.y()),
                                                       QgsPoint(myPosiz.x(),self.startY)]])
                pr.changeGeometryValues({ 0 : geomSquare })
                self.laySez.triggerRepaint()
        else:
            myPosiz = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
            self.startX = myPosiz.x()
            self.startY =myPosiz.y()
            self.drowLine = True

