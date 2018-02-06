# -*- coding: utf-8 -*-
"""
/***************************************************************************
 areadilavoroDialog
                                 A QGIS plugin
 definizione dell'area di lavoro
                             -------------------
        begin                : 2018-01-01
        copyright            : (C) 2018
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
    from PyQt5 import uic
    from PyQt5.QtWidgets import QDialog
except:
    __QGis_version__ = 2
    from PyQt4 import QtCore, QtGui,uic
    from PyQt4.QtGui import QDialog
import os


area_dialog_class = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_areadilavoro.ui'))[0]

       
class areadilavoroDialog(QDialog, area_dialog_class):
    def __init__(self, parent=None):
        super(areadilavoroDialog, self).__init__(parent)
        self.setupUi(self)
