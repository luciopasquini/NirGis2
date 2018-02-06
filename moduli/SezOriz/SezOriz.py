# -*- coding: utf-8 -*-
from qgis.core import *
try:
    __QGis_version__ = 3 
    Qgis.QGIS_VERSION_INT
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt5.QtGui import QIcon,QKeySequence
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu,QMessageBox
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
from qgis.gui import *
import os

class SezOriz:

    def __init__(self, NirGis):
        self.iface = NirGis.iface
        self.NG = NirGis

        
        # VARIABILI DA MODIFICARE PER UN MODULO
        # Nome del modulo e lista delle voci per il menu e per il menu della barra dello strumento
        # Lista self.lstMenu contiene il testo del menu e la funzione richiamata. Un elemento della lista contiene:
        # Nome della voce, funzione richiamata e eventualmente scorciatoia da tastiera (es. F12 per finestra Impianti)
        # La funzione initGiu definirà poi i menu e lo strumento nella toolBar di NirGis
        
        self.nomeDelModulo = u"Sezioni Orizzontali"
        self.versione = "4.0"
        self.sperimentale = False
        self.lstMenu = [
        [u'Calcola',self.run,""],
        [u'Studio Sito',self.startRunStudioCalc,""],
        [u'Calcolo puntuale',self.calcolaLayerPunti,""],
        [u'Calcola Max Campo Edifici',self.startCalcolaMaxEdifici,""],
        [u'Calcola Indicatore Edifici (SOAF)',self.startCalcolaIndicatoriEdifici,""],
        [u"Altezza Critica",self.calcolaAltezzaCritica,""],
        [u"Campo su edifici...",self.calcolaCampoSuEdifici,""]]
    
    def run(self):
        print (u'Calcola..')
    def startRunStudioCalc(self):
        print (u'Studio Sito')
    def calcolaLayerPunti(self):
        print (u'Calcolo puntuale')
    def startCalcolaMaxEdifici(self):
        print (u'Calcola Max Campo Edifici')
    def startCalcolaIndicatoriEdifici(self):
        print (u'SOAF...')
    def calcolaAltezzaCritica(self):
        print (u"Altezza critica")
    def calcolaCampoSuEdifici(self):
        print (u"Campo su edifici")
    def clickStrumento(self):
        print (u"Strumento cliccato")
        
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


        
        
    

