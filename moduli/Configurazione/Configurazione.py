# -*- coding: utf-8 -*-
from qgis.core import *
try:
    __QGis_version__ = 3
    Qgis.QGIS_VERSION_INT
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,QRect
    from PyQt5.QtGui import QIcon,QFont
    from PyQt5.QtWidgets import QAction,QToolBar,QMenu,QFrame,QLabel,QMessageBox
    from PyQt5 import QtCore
    from hashlib import md5
except:
    __QGis_version__ = 2
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4 import QtCore
    import md5
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
import os

import psycopg2
from conf import config
from nirgisversiondialog import nirgisVersionDialog
from configurazioneDialog import configurazioneDialog
from chPassDialog import chPassDialog
import webbrowser
class Configurazione:

    def __init__(self,NirGis):
        self.iface = NirGis.iface
        self.NG = NirGis

        self.nomeDelModulo = u"Configurazione"
        self.versione = "4.0"
        self.sperimentale = False       
        self.lstMenu = [
        ["Configurazione NirGis",self.run,""],
        ["Cambia legende/stili",self.ridefinisciStile,""],
        ["Aiuto",self.apri_wiki,""],
        ["NirGis",self.mostraversione,""]]

        self.url="http://wiki.arpa.veneto.it/index.php/Manuale_utilizzo_NirGis_17.05"
        self.dlg = configurazioneDialog()
        
        dizOpz = {}
        lProv = ["","Belluno","Padova","Rovigo","Treviso","Venezia","Vicenza","Verona"]
        self.codProv = ["0","25","28","29","26","27","24","23"]
        self.dizProv = dict(zip(range(8),zip(self.codProv,lProv)))
        self.dlg.CB_PROVINCIA.insertItems(0,lProv)
        self.dlg.btnCambiaPassword.clicked.connect(self.cambiaPassword)
        self.dbModified = False # per controllare se la connessione deve essere reimpostata
        self.isMultiQmlRun = False # per ridefinizione stile qml
# Definizione del dizionario delle opzioni

#########################################################
# Per inserire una nuova opzione aggiungere una casella di testo QLineEdit o
# una CheckBox nella Finestra di dialogo self.dlg e poi aggiungere una
# riga nel dizionario dizOpz qui sotto.
# Il dizionario deve avere come chiave il nome dell'opzione e
# il contenuto è una lista di 4 valori:
#   0: valore di default della opzione
#   1: Stinga di informazione di default della opzione
#   2: Tipo di opzione "TEXT" se si usa una QLineEdit, "BOOL" se è una QCheckBox e COMBO se è un QComboBox
#   3: l'oggetto di riferimento nella finestra di dialogo
#########################################################

        dizOpz["PROVINCIA_DEFAULT"] = ["","","COMBO",self.dlg.CB_PROVINCIA]
        dizOpz["DB_ADDR"] = ["","","TEXT",self.dlg.DB_ADDR]
        dizOpz["DB_NAME"] = ["","","TEXT",self.dlg.DB_NAME]
        dizOpz["DB_USERNAME"] = ["","","TEXT",self.dlg.DB_USERNAME]
        dizOpz["DB_PASSWORD"] = ["","","TEXT",self.dlg.DB_PASSWORD]
        dizOpz["DB_SCHEMA"] = ["","","TEXT",self.dlg.DB_SCHEMA]
        dizOpz["SAVE_PRG_BEFORE_DB_CONN"] = [True,"","BOOL",self.dlg.SAVE_PRG_BEFORE_DB_CONN]
        dizOpz["CS_INDIRIZZO"] = [False,"","BOOL",self.dlg.CS_INDIRIZZO]
        dizOpz["CS_RESPIMP"] = [False,"","BOOL",self.dlg.CS_RESPIMP]
        dizOpz["CS_NOTE1"] = [False,"","BOOL",self.dlg.CS_NOTE1]
        dizOpz["CS_RESP"] = [False,"","BOOL",self.dlg.CS_RESP]
        dizOpz["CS_ID_PADRE"] = [False,"","BOOL",self.dlg.CS_ID_PADRE]
        dizOpz["CS_NOTE2"] = [False,"","BOOL",self.dlg.CS_NOTE2]
        dizOpz["CS_CREAZIONE"] = [False,"","BOOL",self.dlg.CS_CREAZIONE]
        dizOpz["CS_DATAMODIFY"] = [False,"","BOOL",self.dlg.CS_DATAMODIFY]
        dizOpz["CS_PARERE"] = [False,"","BOOL",self.dlg.CS_PARERE]
        dizOpz["CS_COMUNICAZ"] = [False,"","BOOL",self.dlg.CS_COMUNICAZ]
        dizOpz["CS_DISMISSION"] = [False,"","BOOL",self.dlg.CS_DISMISSION]
        dizOpz["CS_COMUNE"] = [False,"","BOOL",self.dlg.CS_COMUNE]
        dizOpz["CS_PONTE"] = [False,"","BOOL",self.dlg.CS_PONTE]
        dizOpz["CS_POST"] = [False,"","BOOL",self.dlg.CS_POST]
        dizOpz["CS_DISMESSI"] = [False,"","BOOL",self.dlg.CS_DISMESSI]
        dizOpz["PASSO_MAX_CAMPO_ED"] = ["0.5","","TEXT",self.dlg.lePassoMaxEd]
        dizOpz["STILE_EDIFICI_MAX_CAMPO"] = [True,"","BOOL",self.dlg.cbLegMaxCampo]
        dizOpz["STILE_EDIFICI_SEZ_ORIZZ"] = [True,"","BOOL",self.dlg.cbLegSezEd]
        dizOpz["UP_GRONDA"] = ["0.0","","TEXT",self.dlg.leUpGronda]
        dizOpz["ALFA24"] = [True,"","BOOL",self.dlg.ALFA24]
        dizOpz["SAVE_ALL_XML"] = [True,"","BOOL",self.dlg.SAVE_ALL_XML]
        dizOpz["FILE_DTM"] = ["","","TEXT",self.dlg.FILE_DTM]
        dizOpz["CARTELLA_FILE_STILE"] = ["","","TEXT",self.dlg.CARTELLA_FILE_STILE]
        dizOpz["MAX_IMPIANTI_ANT"] = ["100","Massimo numero di siti dove verranno scaricate anche le antenne","TEXT",self.dlg.leMaxImpiantiAnt]
        dizOpz["CAMPOCRITICO"] = ["6.0","Valore di campo utilizzato per calcolare l'altezza critica degli edifici","TEXT",self.dlg.leCampoCritico]
        dizOpz["UPGRONDACRITICO"] = ["2.0","Incremento sulla gronda degli edifici per calcolare l'altezza critica","TEXT",self.dlg.leUpGrondaCritico]
# Fine definizione definizioni delle opzioni
        self.cfg = config(dizOpz)
        # Declare instance attributes

        self.dlg.terstBtn.clicked.connect(self.test_connetti_db)
        self.dlg.fileButton.clicked.connect(self.select_DTM_file)
        self.dlg.stileButton.clicked.connect(self.select_Cartella_Stile)
        self.LastPassoEd = self.dlg.lePassoMaxEd.text()
        self.LastUpGronda = self.dlg.leUpGronda.text()
        self.LastMaxImpiantiAnt = self.dlg.leMaxImpiantiAnt.text()
        self.LastCampoCritico = self.dlg.leCampoCritico.text()
        self.LastUpGrondaCritico = self.dlg.leUpGrondaCritico.text()
        self.dlg.leMaxImpiantiAnt.textChanged.connect(self.aggiornaMaxImpianti)
        self.dlg.lePassoMaxEd.textChanged.connect(self.aggiornaPassoEd)
        self.dlg.leUpGronda.textChanged.connect(self.aggiornaUpGronda)
        self.dlg.leCampoCritico.textChanged.connect(self.aggiornaCampoCritico)
        self.dlg.leUpGrondaCritico.textChanged.connect(self.aggiornaUpGrondaCritico)        
        self.cambioLayEdificiCalc = False
        self.dlg.cb_edifici.currentIndexChanged.connect(self.cambioLayEdifici) # cambia la selezione del layer edifici dal menu a tendina
        self.dlg.cbStatEdifici.stateChanged.connect(self.aggiornaStatEdifici) # cambia il check sulle statistiche degli edifici
        self.dlg.DB_ADDR.textChanged.connect(self.dbModificato)
        self.dlg.DB_SCHEMA.textChanged.connect(self.dbModificato)
        self.dlg.DB_NAME.textChanged.connect(self.dbModificato)
        self.dlg.DB_USERNAME.textChanged.connect(self.dbModificato)
        self.dlg.DB_PASSWORD.textChanged.connect(self.dbModificato)
    def dbModificato(self):
        self.dbModified = True
    def leggiOpzioni(self):
        for j in self.cfg.dOpz:
            if self.cfg.dOpz[j][2] is "TEXT" :
                self.cfg.dOpz[j][3].setText(self.cfg.dOpz[j][0])
            elif self.cfg.dOpz[j][2] is "BOOL" : 
                self.cfg.dOpz[j][3].setChecked(self.cfg.dOpz[j][0])
            elif self.cfg.dOpz[j][2] is "COMBO" :
                if self.cfg.dOpz[j][3] == self.dlg.CB_PROVINCIA:
                    vL = self.cfg.dOpz[j][0]
                    if vL in self.codProv:
                        cIndex = self.codProv.index(vL)
                    else:
                        cIndex = 0
                    self.cfg.dOpz[j][3].setCurrentIndex(cIndex)
        self.dlg.cb_edifici.clear()
        self.dlg.cb_campoidedifici.clear()
        lista_ly_Edifici = [""]
        if __QGis_version__ is 3:
            listaLay = QgsProject.instance().mapLayers().values()
        else:
            listaLay = self.iface.legendInterface().layers()
        for ly in listaLay:
            if ly.type() == QgsMapLayer.VectorLayer:
                lyName = ly.name()
                # Verifica che il layer di edifici non sia il layer Edifici_database_PG
                rifLayer = ly.dataProvider().dataSourceUri()
                noLayrPG = True
                if rifLayer.find("gayatri.arpa.veneto.it")>=0 or rifLayer.find("192.168.31.13")>=0 or rifLayer.find("dbname")>=0 or lyName.find("Edifici_Database_PG")>=0:
                    noLayrPG = False
                if lyName[:5] != "Ed_V_" and lyName[:6] != "DTM_V_" and lyName != "Area di lavoro" and noLayrPG:
                    theFeature = QgsFeature()
                    capture = ly.getFeatures().nextFeature(theFeature)
                    try :
                        theGeometry = theFeature.geometry()
                        if theGeometry.type() == QGis.Polygon:
                            if ly.fieldNameIndex("PIEDE") >= 0:
                                if ly.fieldNameIndex("GRONDA") >= 0:
                                    lista_ly_Edifici.append(lyName)
                    except:
                        pass
        # per popolare il menu a tendina per la scelta degli edifici e la scelta del campo ID per l'edificio visualizzato
        self.dlg.cb_edifici.currentIndexChanged.disconnect()
        
        # self.dlg.cb_campoidedifici.currentIndexChanged.disconnect()
        self.dlg.cb_edifici.insertItems(0,lista_ly_Edifici) # scrive la lista dei layer edifici buoni
        (nomeLy,Trovato) = QgsProject.instance().readEntry("EDIFICI","LYEDIFICI")
        if Trovato:
            if nomeLy in lista_ly_Edifici:
                self.dlg.cb_edifici.setCurrentIndex(lista_ly_Edifici.index(nomeLy)) # si posiziona su quello salvato in automatico
            self.aggiornaStatEdifici() # per scrivere la statistica anche all'avvio...
        self.CampoIDEdifici() # riscrive la lista dei possibili campi ID per il layer edifici scelto
        self.dlg.cb_edifici.currentIndexChanged.connect(self.cambioLayEdifici)
        # self.dlg.cb_campoidedifici.currentIndexChanged.connect()
      



    def cambioLayEdifici(self,numSelL):
    # questa funzione si attiva quando si cambia la scelta del layer edifici
        # bisogna anche azzerare la lista degli ID!!!!
        self.CampoIDEdifici() # per aggiornare la lista dei campi ID e scegliere il campo ID (numerazione degli edifici)
        self.aggiornaStatEdifici()
    def aggiornaStatEdifici(self):
        maxGronda = 0
        maxGronda_Piede = 0
        minPiede = 0
        minPiede_Gronda = 0
        numeroedifici=0       
        if not self.dlg.cbStatEdifici.isChecked():
            self.dlg.leNumEdifici.setText("") # scrive nella finestra il numero di edifici
            self.dlg.leMaxGronda.setText("")
            self.dlg.leMinBase.setText("") 
            return
        nomeLyEd = self.dlg.cb_edifici.currentText()
        if (len(nomeLyEd) == 0 or nomeLyEd==""):
            self.dlg.leNumEdifici.setText("") # scrive nella finestra il numero di edifici
            self.dlg.leMaxGronda.setText("")
            self.dlg.leMinBase.setText("") 
            return
        if __QGis_version__ is 3:
            listLayEd = QgsProject.instance().mapLayersByName(nomeLyEd)
        else:
            listLayEd = QgsMapLayerRegistry.instance().mapLayersByName(nomeLyEd)
        if len(listLayEd) == 0 :
            return
        layEdifici = listLayEd[0]
        idxPiede = layEdifici.fieldNameIndex("PIEDE")
        if idxPiede < 0:
            return
        idxGronda = layEdifici.fieldNameIndex("GRONDA")
        if idxGronda < 0:
            return
        if layEdifici.featureCount() == 0 :
            return
        primoEdifico = True
        for fetc in layEdifici.getFeatures():
            piede = fetc.attributes()[idxPiede]
            gronda = fetc.attributes()[idxGronda]
            numeroedifici+=1
            if primoEdifico :
                maxGronda = gronda
                maxGronda_Piede = piede
                minPiede = piede
                minPiede_Gronda = gronda
                primoEdifico = False
            else:
                if gronda > maxGronda:
                    maxGronda = gronda
                    maxGronda_Piede = piede
                if piede < minPiede:
                    minPiede = piede
                    minPiede_Gronda = gronda
        QgsProject.instance().writeEntry("EDIFICI","MINPIEDE",str(minPiede))
        QgsProject.instance().writeEntry("EDIFICI","MINPIEDEGRONDA",str(minPiede_Gronda))
        QgsProject.instance().writeEntry("EDIFICI","MAXGRONDA",str(maxGronda))
        QgsProject.instance().writeEntry("EDIFICI","MAXGRONDAPIEDE",str(maxGronda_Piede))
        QgsProject.instance().writeEntry("EDIFICI","NUMEDIFICI",str(numeroedifici))
        self.dlg.leNumEdifici.setText(str(numeroedifici)) # scrive nella finestra il numero di edifici
        self.dlg.leMaxGronda.setText(str(maxGronda))
        self.dlg.leMinBase.setText(str(minPiede)) 
    def CampoIDEdifici(self):
        # legge il layer edifici corrente (scelto dal menu a tendina)
        # cerca i possibili campi ID per quel layer e ne carica la lista nel menu
        # a tendina di configurazioni
        self.dlg.cb_campoidedifici.clear()
        nomeLyEdifici = self.dlg.cb_edifici.currentText() # legge quello che e' stato scelto nel menu di scelta dell'edificio
        if (len(nomeLyEdifici)==0 or nomeLyEdifici==""):
            return False
        if __QGis_version__ is 3:
            listLayEdif = QgsProject.instance().mapLayersByName(nomeLyEdifici)
        else:
            listLayEdif = QgsMapLayerRegistry.instance().mapLayersByName(nomeLyEdifici)
        layEdif = listLayEdif[0]
        fields = layEdif.pendingFields()
        field_names = [field.name() for field in fields] # lista con i nomi dei campi nel layer edifici
        indicicattivi=('MAXCAMPO','XMAXCAMPO','YMAXCAMPO','ZMAXCAMPO','PIEDE','GRONDA','PAR_MAX','COLORESEZ','INDICATORE','E_MEDIO')
        campibuoni=[]
        campibuoni.append("")
        i = 0
        for i in range(0,len(field_names)):
            if field_names[i] not in indicicattivi: # non e' un indice cattivo
            # verifico se i campi sono buoni (ne estraggo i valori)
                edificilayer = layEdif.getFeatures() # elenco degli edifici del layer edifici (geometria+attributi)
                indicecampo = layEdif.fieldNameIndex(field_names[i]) # numero che indica la posizione del campo da testare nella tabella del layer (da 0...)
                listatest=[]
                ok = False
                for edificio in edificilayer:
                    attuale=edificio[indicecampo] # e' il potenziale valore dell'ID associato all'edificio corrente nel ciclo for
                    if attuale not in listatest: # se ci sono valori doppi esce dal ciclo
                        listatest.append(attuale)
                        ok = True
                    else:
                        ok = False # appena c'e' un doppio non e' un campo ID buono
                        break
                if ok: campibuoni.append(field_names[i]) # lista dei campi per popolare la lista
        # sel la lista e' vuota o ha solo il valore "" allora manca un campo identificatiivo valido e va creato
        if len(campibuoni)<2: # non c'e' neanche un campo buono per l'ID
        # scrivio io l'ID
            if __QGis_version__ is 3:
                listLayEdif = QgsProject.instance().mapLayersByName(nomeLyEdifici)
            else:
                listLayEdif = QgsMapLayerRegistry.instance().mapLayersByName(nomeLyEdifici)
            layEdifici = listLayEdif[0]
            id_numedificio = layEdifici.fieldNameIndex(u'ID')
            modificaPermessa = layEdifici.dataProvider().capabilities()
            if id_numedificio<0: # se non c'e' un ID lo crea
                if (modificaPermessa & QgsVectorDataProvider.AddAttributes):
                    if layEdifici.dataProvider().addAttributes([QgsField(u'ID',QVariant.Int)]):
                        layEdifici.updateFields() # aggiorno (si aggiunge il campo "ID")
                        id_numedificio =  layEdifici.fieldNameIndex(u'ID') # assegno il nome del campo aggiungendolo all'elenco dei nomi del campo
                        campibuoni.append(u'ID') # lo metto nell'elenco!
                if (not modificaPermessa) or (id_numedificio<0):
                    QMessageBox.warning(self.iface.mainWindow(), "Errore","Non posso aggiungere l'ID al layer, verificare le protezioni di scrittura del file. ",QMessageBox.Ok, QMessageBox.Ok)
                else:
                    listarighe = layEdifici.getFeatures()
                    numid=1
                    for riga in listarighe:
                        layEdifici.dataProvider().changeAttributeValues({riga.id():{id_numedificio:numid}})
                        numid+=1
            else: # c'e' un campo che si chiama ID ma non va bene (altrimenti sarebbe bella lista dei campibuoni
                QMessageBox.warning(self.iface.mainWindow(), "Errore","Non ci sono campi  validi per identificare gli edifici del layer\ned e' presente un campo chiamato ID ma con valori doppi:\nnon e' possibile creare un campo ID in automatico.", QMessageBox.Ok, QMessageBox.Ok) 
                QMessageBox.warning(self.iface.mainWindow(), "Attenzione","Scegliere un altro layer edifici o chiudere la plugin configurazione,\ncancellare manualmente il campo ID dal layer edifici scelto\ne riaprire la configurazione per permettere la creazione di un nuovo ID.", QMessageBox.Ok, QMessageBox.Ok) 
                return False
        # Scrivo nel menu a tendina dell'ID
        # self.dlg.cb_campoidedifici.currentIndexChanged.disconnect() # da errore messa qui
        self.dlg.cb_campoidedifici.insertItems(0,campibuoni) # inserisce nel menu per la scelta degli edifici la lista degli stessi
        # se trova un campo gia' scelto in precedenza e questo fa parte della lista dei campi buoni,
        # si posiziona su quel campo!
        (nomeIDLy,Trovato2) = QgsProject.instance().readEntry("EDIFICI","CAMPOIDLYEDIFICI") # legge l'eventuale campo memorizzato in precedenza
        if Trovato2:
            if nomeIDLy in campibuoni:
                self.dlg.cb_campoidedifici.setCurrentIndex(campibuoni.index(nomeIDLy)) # si posiziona su quello salvato in automatico            
       
        return True
    

    def aggiornaUpGrondaCritico(self):
        tVal = self.dlg.leUpGrondaCritico.text()
        try:
            fVal = float(tVal)
        except ValueError:
            self.dlg.leUpGrondaCritico.setText(self.LastUpGrondaCritico)
            return
        self.LastUpGrondaCritico = tVal 
    def aggiornaCampoCritico(self):
        tVal = self.dlg.leCampoCritico.text()
        try:
            fVal = float(tVal)
        except ValueError:
            self.dlg.leCampoCritico.setText(self.LastCampoCritico)
            return
        self.LastCampoCritico = tVal
    def aggiornaUpGronda(self):
        tVal = self.dlg.leUpGronda.text()
        try:
            fVal = float(tVal)
        except ValueError:
            self.dlg.leUpGronda.setText(self.LastUpGronda)
            return
        self.LastUpGronda = tVal
    def aggiornaPassoEd(self):
        tVal = self.dlg.lePassoMaxEd.text()
        try:
            fVal = float(tVal)
        except ValueError:
            self.dlg.lePassoMaxEd.setText(self.LastPassoEd)
            return
        self.LastPassoEd = tVal
    def aggiornaMaxImpianti(self):
        tVal = self.dlg.leMaxImpiantiAnt.text()
        try:
            iVal = int(tVal)
            self.dlg.leMaxImpiantiAnt.setText(str(iVal))
        except ValueError:
            self.dlg.leMaxImpiantiAnt.setText(self.LastMaxImpiantiAnt)
            return
        self.LastMaxImpiantiAnt = tVal
    def select_Cartella_Stile(self):
       theFolder = QFileDialog.getExistingDirectory(self.dlg,"Apri la cartella degli stili",os.environ['HOME'])
       if len(theFolder) > 0 :
          self.dlg.CARTELLA_FILE_STILE.setText(theFolder)
    def select_DTM_file(self):
       theFile = QFileDialog.getOpenFileName(self.dlg,"Open Image",os.environ['HOME'],"File Tiff o hdr.adf (*.tiff *.tif *.adf);;Tutti i file (*)")
       if len(theFile) > 0 :
          self.dlg.FILE_DTM.setText(theFile)      
    def test_connetti_db(self):
        if __QGis_version__ is 3:
            thePwd = md5(self.dlg.DB_PASSWORD.text().encode()).hexdigest()
        else:
            thePwd = md5.new(self.dlg.DB_PASSWORD.text()).hexdigest()
        try:
           comd = "host="+self.dlg.DB_ADDR.text()+" dbname="+self.dlg.DB_NAME.text()+" user="+self.dlg.DB_USERNAME.text()
           comd = comd + " password="+thePwd+" connect_timeout=8"
           connessione = psycopg2.connect(comd)
        except:
            try:
                comd = "host="+self.dlg.DB_ADDR.text()+" dbname="+self.dlg.DB_NAME.text()+" user="+self.dlg.DB_USERNAME.text()
                comd = comd + " password="+self.dlg.DB_PASSWORD.text()+" connect_timeout=8"
                connessione = psycopg2.connect(comd)
                cur = connessione.cursor()
                cmd = "ALTER USER "+self.dlg.DB_USERNAME.text()+" WITH PASSWORD '"+thePwd+"';"
                cur.execute(cmd)
                connessione.commit()                
            except:
                QMessageBox.warning(self.dlg, "Problemi di connessione","Errore di connessione con il Database", QMessageBox.Ok, QMessageBox.Ok)
                return False
        self.test_Provincia(connessione)
        connessione.close()
        QMessageBox.warning(self.dlg, "Connessione a Database","Collegamento OK", QMessageBox.Ok, QMessageBox.Ok)
        return True
    def run(self):
        self.leggiOpzioni()
        result = self.dlg.exec_()
        if result == 1:
            self.scriviOpzioni()
            if self.dbModified:
                try:
                    if self.NG.CS.con != None:
                        self.NG.CS.con.close()
                        self.NG.CS.checkDbConnection()
                except:
                    QMessageBox.warning(self.iface.mainWindow(), "Attenzione","Non è stata aggiornata la connessione al DB\n riavviare QGIS!", QMessageBox.Ok, QMessageBox.Ok)
    def scriviOpzioni(self):
        nomeLyEdifici = self.dlg.cb_edifici.currentText() # legge il dato dal menu a tendina degli edifici
        nomeCampoID = self.dlg.cb_campoidedifici.currentText() # legge quello che e' stato scelto nel menu di scelta del campo da usare per identificare l'edificio
        if __QGis_version__ is 3:
            listLayEdif = QgsProject.instance().mapLayersByName(nomeLyEdifici)
        else:
            listLayEdif = QgsMapLayerRegistry.instance().mapLayersByName(nomeLyEdifici)
        if len(listLayEdif) > 0 :
          layEdif = listLayEdif[0]
          idx_color = layEdif.fieldNameIndex('COLORESEZ')
          # se manca aggiungere il campo COLORESEZ
          if idx_color < 0 :
             modificaPermessa = layEdif.dataProvider().capabilities()
             if modificaPermessa & QgsVectorDataProvider.AddAttributes:
                if layEdif.dataProvider().addAttributes([QgsField('COLORESEZ',QVariant.Int)]):
                   layEdif.updateFields()
                   idx_color = layEdif.fieldNameIndex('COLORESEZ')
                if (not modificaPermessa) or (idx_color < 0):
                   QMessageBox.warning(self.iface.mainWindow(), "Errore","Non posso utilizzare il layer, verificare le protezioni di scrittura del file. ", QMessageBox.Ok, QMessageBox.Ok) 
                #else:
                #   QgsProject.instance().writeEntry("EDIFICI","LYEDIFICI",nomeLyEdifici)
        QgsProject.instance().writeEntry("EDIFICI","LYEDIFICI",nomeLyEdifici)
        QgsProject.instance().writeEntry("EDIFICI","CAMPOIDLYEDIFICI",nomeCampoID) # EDIFICI = nome della plugin cui viene assegnata la variabile globale CAMPOIDLYEDIFICI col valore nomeCampoID
        for j in self.cfg.dOpz:
          if self.cfg.dOpz[j][2] is "TEXT" :
              self.cfg.dOpz[j][0] = self.cfg.dOpz[j][3].text()
          elif self.cfg.dOpz[j][2] is "BOOL" : 
              self.cfg.dOpz[j][0] = self.cfg.dOpz[j][3].isChecked()
          elif self.cfg.dOpz[j][2] is "COMBO" :
              if self.cfg.dOpz[j][3] == self.dlg.CB_PROVINCIA:
                  cIndex = self.cfg.dOpz[j][3].currentIndex()
                  self.cfg.dOpz[j][0] = self.codProv[cIndex]
        self.cfg.salvaFileOpzioni()

    def ridefinisciStile(self):
        pass
    def apri_wiki(self):
        webbrowser.open_new(self.url)
    def mostraversione(self):
        dlgVersion = nirgisVersionDialog()
        yLine = 260
        
        font = QFont()
        font.setPointSize(10)
        nomiModuli = list(self.NG.Moduli.keys())
        nomiModuli.sort()
        for nomeModulo in nomiModuli:
            modNG = self.NG.Moduli[nomeModulo]
            theFrame = QFrame(dlgVersion)
            theFrame.setGeometry(QRect(100, yLine, 24, 24))
            theFrame.setStyleSheet(_fromUtf8("image: url("+modNG.icon_path+");"))
            theFrame.setFrameShape(QFrame.StyledPanel)
            theFrame.setFrameShadow(QFrame.Raised)
            theFrame.setLineWidth(0)
            
            theLabelName = QLabel(dlgVersion)
            theLabelName.setFont(font)
            theLabelName.setObjectName(_fromUtf8("label_"+modNG.nomeDelModulo))
            theLabelName.setGeometry(QRect(130, yLine+4, 120, 16))
            theLabelName.setText(modNG.nomeDelModulo)

            theLabelVer = QLabel(dlgVersion)
            theLabelVer.setFont(font)
            theLabelVer.setObjectName(_fromUtf8("label_Ver_"+modNG.nomeDelModulo))
            theLabelVer.setGeometry(QRect(320, yLine+4, 50, 16))
            theLabelVer.setText(modNG.versione)
            
            if modNG.sperimentale:
                theLabelVer = QLabel(dlgVersion)
                theLabelVer.setFont(font)
                theLabelVer.setObjectName(_fromUtf8("label_Sperimentale_"+modNG.nomeDelModulo))
                theLabelVer.setGeometry(QRect(350, yLine+4, 100, 16))
                theLabelVer.setText("Sperimentale")
            yLine += 35
        dlgVersion.okButton.setGeometry(QRect(610, yLine, 90, 30))
        dlgVersion.setFixedWidth(720)
        dlgVersion.setFixedHeight(yLine+45)
        result = dlgVersion.exec_()
        del dlgVersion
    def clickStrumento(self):
        self.run()
    def cambiaPassword(self):
        cambiaPasswdDlg = chPassDialog()
        result = cambiaPasswdDlg.exec_()
        if result == 1:
            comd_ini = "host="+self.dlg.DB_ADDR.text()+" dbname="+self.dlg.DB_NAME.text()+" user="+self.dlg.DB_USERNAME.text()
            if cambiaPasswdDlg.newPassED.text() != cambiaPasswdDlg.confNewPassED.text():
                QMessageBox.warning(self.dlg, "Password",
                u"La nuova Password è diversa dalla\n nuova Password di conferma",QMessageBox.Ok, QMessageBox.Ok)
                return
            theOldPwd = md5.new(cambiaPasswdDlg.oldPassED.text()).hexdigest()
            theNewPwd = md5.new(cambiaPasswdDlg.newPassED.text()).hexdigest()
            try:
                comd = comd_ini + " password="+theOldPwd+" connect_timeout=8"
                connessione = psycopg2.connect(comd)
            except Exception as e:
                QMessageBox.warning(self.dlg, "Problemi di connessione",u"Forse è sbagliata la vecchia password\n"+str(e), QMessageBox.Ok, QMessageBox.Ok)
                return
            try:
                cur = connessione.cursor()
                cmd = "ALTER USER "+self.dlg.DB_USERNAME.text()+" WITH PASSWORD '"+theNewPwd+"';"
                cur.execute(cmd)
                connessione.commit()
                self.dlg.DB_PASSWORD.setText(cambiaPasswdDlg.newPassED.text())
                self.scriviOpzioni()
                connessione.close()
                comd = comd_ini + " password="+theNewPwd+" connect_timeout=8;"
                connessione = psycopg2.connect(comd)
                self.test_Provincia(connessione)
                connessione.close()
                QMessageBox.warning(self.dlg, "Cambio Password","Password Modificata", QMessageBox.Ok, QMessageBox.Ok)
            except Exception as e:
                QMessageBox.warning(self.dlg, "Problemi di connessione","Errore nella modifica della password\n"+str(e), QMessageBox.Ok, QMessageBox.Ok)
        del cambiaPasswdDlg
    def test_Provincia(self,conn):
        try:
            Schema = self.cfg.dOpz["DB_SCHEMA"]
            cur = conn.cursor()
            cmd = "SELECT gid FROM "+Schema+".diz_utenti WHERE uname='"+self.dlg.DB_USERNAME.text()+"'"

            cur.execute(cmd)
            tIn = cur.fetchall()
            gidDB = tIn[0][0]
            if gidDB > 0:
                cmd = "SELECT idprov FROM "+Schema+".dec_province AS p,"+Schema+".diz_gruppi AS g WHERE p.provincia=g.gname and g.gid="+str(gidDB)+";"
                cur.execute(cmd)
                codP = str(cur.fetchall()[0][0])
                if codP in self.codProv:
                    indC = self.codProv.index(codP)
                else:
                    indC = 0
                self.cfg.dOpz["PROVINCIA_DEFAULT"][3].setCurrentIndex(indC)                
        except:
            pass
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

