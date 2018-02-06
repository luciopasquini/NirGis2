# -*- coding: utf-8 -*-
"""
/***************************************************************************
 nirgis
                                 A QGIS plugin
 NirGis plugins
                              -------------------
        begin                : 2017-12-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by NirGis Group
        email                : lucio.pasquini@arpa.veneto.it
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
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt4.QtGui import QIcon,QAction,QToolBar,QMenu


# Initialize Qt resources from file resources.py
from .resources import *

import os.path
import imp
import sys
class nirgis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.versione = "18.04.0"
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)
        # initialize local variable
        self.Moduli = {}
        self.Conf = None
        self.CS = None
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'nirgis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate('nirgis', message)

    def initGui(self):

        # Istanza di una nuova toolbar (barra strumenti) NirGis
        self.toolbarNirGis = self.iface.mainWindow().findChild(QToolBar, u'NirGis')
        if not self.toolbarNirGis:
            self.toolbarNirGis = self.iface.addToolBar(u'NirGis')
            self.toolbarNirGis.setObjectName(u'NirGis')

        # Nuovo menu NirGis nella barra dei menu 
        menuBar = self.iface.mainWindow().menuBar()
        self.menuNirGis = menuBar.addMenu('&NirGis')

        # Ricerca dei moduli nella sotto cartella moduli
        moduli_path = os.path.join(self.plugin_dir,"moduli")
        for dMod in os.listdir(moduli_path):
            dir_mod = os.path.join(moduli_path,dMod)
            if os.path.isdir(dir_mod):
                if dir_mod not in sys.path:
                    sys.path.append(dir_mod)
                fMod = os.path.join(dir_mod,dMod+".py")
                if os.path.isfile(fMod):
                    theModule = imp.load_source(dMod,fMod)
                    inClass = getattr(theModule,dMod)
                    # istanzia il modulo e lo inizializza
                    theClass = inClass(self)
                    self.Moduli[dMod] = theClass
                    theClass.initGui()
                    
        self.Conf = self.Moduli.get("Configurazione",None)
        self.CS = self.Moduli.get("CaricaSiti",None)
    def getOpz(self,nomOpz):
        if self.Conf:
            if nomOpz in self.Conf.cfg.dOpz.keys():
                if self.Conf.cfg.dOpz[nomOpz][2] is "TEXT":
                    return self.Conf.cfg.dOpz[nomOpz][0]
                elif self.Conf.cfg.dOpz[nomOpz][2] is "BOOL":
                    return self.Conf.cfg.dOpz[nomOpz][0]
                elif self.Conf.cfg.dOpz[nomOpz][2] is "COMBO":
                    return int(self.Conf.cfg.dOpz[nomOpz][0])
        return None
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        del self.toolbarNirGis
        self.iface.mainWindow().menuBar().removeAction(self.menuNirGis.menuAction())

