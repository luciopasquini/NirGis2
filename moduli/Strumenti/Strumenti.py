# -*- coding: utf-8 -*-
from qgis.core import *
try:
    __QGis_version__ = 3
    Qgis.QGIS_VERSION_INT
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt5.QtGui import QIcon,QKeySequence
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
import os

class Strumenti:

    def __init__(self, NirGis):
        self.iface = NirGis.iface
        self.NG = NirGis

        
        # VARIABILI DA MODIFICARE PER UN MODULO
        # Nome del modulo e lista delle voci dei menu e menu della barra dello strumento
        # Lista self.lstMenu contiene il testo del menu e la funzione richiamata. Un elemento della lista contiene:
        # Nome della voce, funzione richiamata e eventualmente scorciatoia da tastiera (es. F12 per finestra Impianti)
        # La funzione initGiu definirà poi i menu e lo strumento nella toolBar di NirGis
        self.nomeDelModulo = u"Strumenti"
        self.versione = "4.0"
        self.sperimentale = True
        self.lstMenu = [
        [u'Report Impianti',self.run,""],
        [u'Report Impianti RB1',self.leggiRB1,""],
        [u'CTRN - Geoportale Veneto',self.aprigeoportale,""]]

    def clickStrumento(self):
        print (u"Strumento cliccato")    
    def run(self):
        print (u'Report Impianti')
    def leggiRB1(self):
        print (u'Report Impianti RB1')
    def aprigeoportale(self):
        print (u'CTRN - Geoportale Veneto')
        
    def tr(self, message):
        return QCoreApplication.translate('nirgis', message)
    def initGui(self):

        self.icon_path = os.path.join(os.path.dirname(__file__),"icon.png") 
        
        strumento = QAction(QIcon(self.icon_path),self.tr(self.nomeDelModulo),self.iface.mainWindow())
        strumento.triggered.connect(self.clickStrumento)
        
        if len(self.lstMenu) > 0:
            menuModulo = self.NG.menuNirGis.addMenu(QIcon(self.icon_path),self.tr(self.nomeDelModulo))
            for vMenu in self.lstMenu:
                action = QAction(vMenu[0],menuModulo)
                action.triggered.connect(vMenu[1])
                if len(vMenu[2]) > 0:
                    action.setShortcut(QKeySequence(vMenu[2]))
                menuModulo.addAction(action)
            strumento.setMenu(menuModulo)
        else:
            self.NG.menuNirGis.addAction(strumento)            
        self.NG.toolbarNirGis.addAction(strumento)


        
        
    

