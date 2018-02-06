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
import platform
import shutil
import numpy
from osgeo import gdal
from osgeo import osr
from areadilavoroDialog import areadilavoroDialog
from squareFreeHand import squareFreeHand
class AreaLavoro:

    def __init__(self, NirGis):
        self.iface = NirGis.iface
        self.NG = NirGis
        
        # VARIABILI DA MODIFICARE PER UN MODULO
        # Nome del modulo e lista delle voci dei menu e menu della barra dello strumento
        # Lista self.lstMenu contiene il testo del menu e la funzione richiamata. Un elemento della lista contiene:
        # Nome della voce, funzione richiamata e eventualmente scorciatoia da tastiera (es. F12 per finestra Impianti)
        # La funzione initGiu definirà poi i menu e lo strumento nella toolBar di NirGis
        
        self.nomeDelModulo = u"AreaLavoro"
        self.versione = "4.0"
        self.sperimentale = False
        self.modulo_dir = os.path.dirname(__file__)       
        self.lstMenu = []
        self.dlg = areadilavoroDialog()
        self.squareFreeHand = squareFreeHand(self.iface,None)
        self.SistemaOperativo = platform.system() # restituisce 'Linux', 'Windows' o 'Java'
    def clickStrumento(self):
        if __QGis_version__ == 3:
            myQgsMapLayerRegistry = QgsProject.instance()
        else:
            myQgsMapLayerRegistry = QgsMapLayerRegistry.instance()
        # Controllo se è stato salvato un progetto per avere a disposizione la cartella di destinazione dei files
        if len(QgsProject.instance().fileName()) == 0:
            QMessageBox.warning(self.iface.mainWindow(), "Informazioni","Prima di definire l'area di lavoro apri un progetto\n oppure salva un nuovo progetto\n in una cartella di lavoro.", QMessageBox.Ok, QMessageBox.Ok)
            return        
        # Se esistono dei layer "Area di lavoro" con lo stesso nome vengono rimossi dalla legenda
        listL = myQgsMapLayerRegistry.mapLayersByName("Area di lavoro")
        print ("Lista delle aree di lavoro")
        print (listL)
        print ("Fine Lista delle aree di lavoro")    
        for j in listL[1:]:
            myQgsMapLayerRegistry.removeMapLayer(j.id())
            del j
        # Sposta l'area di lavoro se è gia presente il layer 
        if len(listL) == 1:
            self.squareFreeHand.startSquareDraw(listL[0])
            return
        listLaySiti = myQgsMapLayerRegistry.mapLayersByName("Impianti")
        if len(listLaySiti) > 0 :
            laySiti = listLaySiti[0]
            # Controllo se è stato selezionato un sito nel Layer siti
            if laySiti.selectedFeatureCount() > 0 :
                # Richiesta con finestradi dialogo della dimensione dell'area di lavoro
                self.dlg.show()
                result = self.dlg.exec_()
                if result != 1:
                    return
                srtDistanza = self.dlg.editDim.text()
                strDistInfluenza = self.dlg.editInfluenza.text()
                try:
                    distanza = float(srtDistanza)
                    distInfluenza = float(strDistInfluenza)
                except ValueError:
                    QMessageBox.warning(self.iface.mainWindow(), "Errore","Errore nel numero inserito", QMessageBox.Ok, QMessageBox.Ok)
                    return
                # uso del primo sito selezionato per definire l'area di lavoro
                fecSelList = laySiti.selectedFeatures()                    
                geom = fecSelList[0].geometry()
                punto = geom.asPoint()
                px = punto.x()
                py = punto.y()
                self.def_area(px,py,distanza,distInfluenza)
            else :
                QMessageBox.warning(self.iface.mainWindow(), "Informazioni","Per definire l'area di lavoro selezionare\n un impianto nel layer Impianti", QMessageBox.Ok, QMessageBox.Ok)
        else :
            QMessageBox.warning(self.iface.mainWindow(), "Informazioni","Per definire l'area di lavoro deve\n essere presente il layer Impianti\n con un impianto selezionato", QMessageBox.Ok, QMessageBox.Ok)
    def def_area(self,x,y,dist,distInfluenza):
        if __QGis_version__ == 3:
            myQgsMapLayerRegistry = QgsProject.instance()
        else:
            myQgsMapLayerRegistry = QgsMapLayerRegistry.instance()       
        # Funzione per definire l'area di lavoro partendo dalle coordinate centrali e dalla dimensione (dist*2)
        # Se esistono dei layer "Area di lavoro" vengono rimossi dalla legenda
        listL = self.iface.mapCanvas().layers()  
        for j in listL :
            if j.name() == "Area di lavoro" :
                myQgsMapLayerRegistry.removeMapLayer(j.id())
                del j
        # Istanza di un layer 
        vl = QgsVectorLayer("polygon?crs=epsg:3003", "Area di lavoro", "memory")
        pr = vl.dataProvider()
        fet = QgsFeature()
        fetInfluenza = QgsFeature()
        # Arrotondamenti a 2 decimali per evitare problemi
        x = round(x,2)
        y = round(y,2)
        dist = round(dist,2)
        distInfluenza = round(distInfluenza,2)
        if __QGis_version__ == 3:
            areaAnalisi = QgsGeometry.fromPolygonXY( [ [ QgsPointXY(x-dist,y-dist),QgsPointXY(x-dist,y+dist),QgsPointXY(x+dist,y+dist),QgsPointXY(x+dist,y-dist) ] ] )            
        else:
            areaAnalisi = QgsGeometry.fromPolygon( [ [ QgsPoint(x-dist,y-dist),QgsPoint(x-dist,y+dist),QgsPoint(x+dist,y+dist),QgsPoint(x+dist,y-dist) ] ] )

        areaInfluenza = areaAnalisi.buffer(distInfluenza,30)
        fet.setGeometry(areaAnalisi)
        fetInfluenza.setGeometry(areaInfluenza)
        pr.addFeatures( [ fet,fetInfluenza ] )

        vl.commitChanges()

        nomeDir = os.path.dirname(QgsProject.instance().fileName())
        nomeFileArea = os.path.join(nomeDir,"areadilavoro.shp")
        theCoor= QgsCoordinateReferenceSystem(3003,QgsCoordinateReferenceSystem.EpsgCrsId)
        error = QgsVectorFileWriter.writeAsVectorFormat(vl,nomeFileArea,"CP1250", theCoor, "ESRI Shapefile")
        fileqmla = os.path.join(nomeDir,"areadilavoro.qml")
        if not os.path.isfile(fileqmla):
            filesrcqmla = os.path.join(self.modulo_dir,"areadilavoro.qml")
            shutil.copyfile(filesrcqmla,fileqmla)
        vlayer = QgsVectorLayer(nomeFileArea, "Area di lavoro", "ogr")
        myQgsMapLayerRegistry.addMapLayer(vlayer)
        del vl
        listLayDTM = myQgsMapLayerRegistry.mapLayersByName("DTM") # cerco i layer che si chiamano DTM nella lista dei raster nella legenda
        if len(listLayDTM) == 0 : # se nella legenda non ci sono raster chiamati DTM allora prende quello memorizzato in "configurazione.xml"
            self.getDTM() # e lo taglia all'interno dell'area di lavoro

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

    def getDTM(self):
        
    # Funzione per estrarre il la parte del DTM all'interno dell'area di lavoro
        fileGlobDTM = self.NG.getOpz("FILE_DTM")
        if __QGis_version__ is 3:
            listLayArea = QgsProject.instance().mapLayersByName("Area di lavoro")
        else:
            listLayArea = QgsMapLayerRegistry.instance().mapLayersByName("Area di lavoro")
        if len(listLayArea) > 0 :
            layArea = listLayArea[0]            
            itero = layArea.getFeatures()
            fecl = QgsFeature()
            itero.nextFeature(fecl)
            geom = fecl.geometry()
            poligono = geom.asPolygon()
            xmin = poligono[0][0].x()
            xmax = xmin
            ymin = poligono[0][0].y()
            ymax = ymin
            for k in poligono[0]:
                if k.x() < xmin:
                    xmin = k.x()
                if k.x() > xmax:
                    xmax = k.x()
                if k.y() < ymin:
                    ymin = k.y()
                if k.y() > ymax:
                    ymax = k.y()

            #Apertura del file raster originale e lettura dei suoi parametri
            inDTM = gdal.Open(fileGlobDTM)
            if inDTM is None:
                QMessageBox.warning(self.iface.mainWindow(), "Informazioni","Manca il file DTM:  " + fileGlobDTM, QMessageBox.Ok, QMessageBox.Ok)
                return
            rows = inDTM.RasterYSize
            cols = inDTM.RasterXSize

            vDataDTM = inDTM.GetGeoTransform()
            xOrigin = vDataDTM[0]
            yOrigin = vDataDTM[3]
            pixelWidth = vDataDTM[1]
            pixelHeight = vDataDTM[5]

            # Calcolo del numero di celle del raster da estrarre e delle coordinate di spostaamento offset
            xoff = int((xmin - xOrigin)/pixelWidth)
            yoff = int((yOrigin - ymax)/pixelWidth)
            xcount = int((xmax - xmin)/pixelWidth)+1
            ycount = int((ymax - ymin)/pixelWidth)+1

            # Controllo che l'intervallo calcolato non esca dai limiti del raster originale ed
            # eventualmente vengono ridefiniti i limiti
            if xoff < 0:
                xcount = xcount + xoff
                xoff = 0
            if xoff > cols -1:
                xoff = cols -1
                xcount = 0
            if yoff < 0:
                ycount = ycount + yoff
                yoff = 0
            if yoff > rows -1:
                yoff = rows -1
                ycount = 0
            if xoff + xcount > cols -1:
                xcount = cols -1 - xoff
            if yoff + ycount > rows -1:
                ycount = rows -1 - yoff
            if xoff + xcount < 0:
                xcount = 0
            if yoff + ycount < 0:
                ycount = 0

            # se non ci sono dati da estrarre ycount e xcount uguali a zero uscita dalla funzione
            if xcount == 0 or ycount == 0 :
                return

            # ridefinizione delle coordinate del punto di origine della parte di raster
            # estratta per fare in modo che si sovrapponga esattamente all'originale 
            redef_xmin = xoff * pixelWidth + xOrigin
            redef_ymax = yOrigin - yoff * pixelWidth  
            
            # taglio, riproiezione e ricampionamento con passo 1m x 1m
            nomeDir = os.path.dirname(QgsProject.instance().fileName())
            nomeFileDTMtiff = os.path.join(nomeDir,"DTM.tiff")
            fileNomeAAIGrid = os.path.join(nomeDir,"DTM.asc")
            
            if self.SistemaOperativo=='Linux':
                # estrazione dal raster della matrice di valori di interesse
                myband = inDTM.GetRasterBand(1)
                elev_data = myband.ReadAsArray(xoff,yoff,xcount,ycount).astype(numpy.float)

                # istanza al nuovo raster nella RAM e inserimento della matrice di valori
                target_mem = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Float32)
                target_mem.SetGeoTransform((redef_xmin, pixelWidth, 0,redef_ymax, 0, pixelHeight))
                outBand = target_mem.GetRasterBand(1)
                outBand.SetNoDataValue(-9999)
                outBand.WriteArray(elev_data)
                outBand.FlushCache()
                drivergrid = gdal.GetDriverByName("AAIGrid")
                outRast_dg = drivergrid.CreateCopy(fileNomeAAIGrid, target_mem, 0 )

                # scrittura del DTM estratto in un file GeoTiff
                drivertiff = gdal.GetDriverByName("GTiff")
                nomeFileDTMtiff = os.path.join(nomeDir,"DTM.tiff")
                dtm_ds = drivertiff.CreateCopy( nomeFileDTMtiff, target_mem, 0 )
                #imposta la proj a Gauss  Boaga fuso Ovest 3003
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3003)
                sr_wkt = sr.ExportToWkt()
                dtm_ds.SetProjection(sr_wkt)
                # chiusura dei raster necessaria per terminare la scrittura
                dtm_ds = None
                outRast_dg = None
                inDTM = None
                target_mem = None
            else: # sistemi operativi Windows
                gdal.SetConfigOption('GTIFF_VIRTUAL_MEM_IO','IF_ENOUGH_RAM') # usa tutta la RAM se necessario, per leggere GeoTiff...
                # if gdal.GetCacheMax()<500000000: gdal.SetCacheMax(500000000)
                command_cut = "gdal_translate -of GTiff -projwin "+str(redef_xmin)+" "+str(redef_ymax)+" "+str(xmax)+" "+str(ymin)+" -a_srs EPSG:3003 -r bilinear -tr 1 1 "+fileGlobDTM+" "+nomeFileDTMtiff
                subprocess.call(command_cut)
                dtm_ds = gdal.Open(nomeFileDTMtiff) # aggiunta con nuovi comandi 20/04/2017
                #imposta la proj a Gauss  Boaga fuso Ovest 3003
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3003)
                sr_wkt = sr.ExportToWkt()
                dtm_ds.SetProjection(sr_wkt)
                # scrittura dei dati del DTM estratto in un file Asci Arc/info
                command_translatetoasc= "gdal_translate -of AAIGrid "+nomeFileDTMtiff+" "+fileNomeAAIGrid
                subprocess.call(command_translatetoasc)
                # chiusura dei raster necessaria per terminare la scrittura
                dtm_ds = None
                inDTM = None

            # lettura de file DTM estrattocome GeoTiff e caricamento come layer
            rlayer = QgsRasterLayer(nomeFileDTMtiff, "DTM")
            # definire il file stile per il DTM
            #fileqmla = os.path.join(nomeDir,"dtm.qml")
            #if not os.path.isfile(fileqmla):
            #   filesrcqmla = os.path.join(self.plugin_dir,"dtm.qml")
            #   shutil.copyfile(filesrcqmla,fileqmla)
            #rlayer.loadNamedStyle(fileqmla)
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            
        
        
    

