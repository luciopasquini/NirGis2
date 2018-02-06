import os
import shutil
import datetime
from types import *
import collections
import xml.etree.ElementTree as ET
class config:

    def __init__(self,dizOpzioni):
      self.nomeFile = os.path.join(os.environ['HOME'],"configurazione.xml") # HOME va sempre bene solo per Linux ma per Windows potrebbe non andar bene!!!
       # self.nomeFile = os.path.join(os.path.expanduser('~'),"configurazione.xml") # questo e' il percorso C:\Users\mscola... per me in Windows
      if not os.path.isfile(self.nomeFile): # se non trova il file
          filesrcqmla = os.path.join(os.path.dirname(__file__),"configurazione.xml")
          shutil.copyfile(filesrcqmla,self.nomeFile)      
      self.dOpz = dizOpzioni
      self.leggiFileOpzioni()

    def leggiFileOpzioni(self):
        xmldoc = ET.parse(self.nomeFile)
        rootNode = xmldoc.getroot()
        for nomeOpz in rootNode:
            valore = nomeOpz.get("value","")
            if valore == 'True':
                valore = True
            elif valore == 'False' :
                valore = False
            info = nomeOpz.get("inf","")
            if nomeOpz.tag in self.dOpz.keys():
                self.dOpz[nomeOpz.tag][0] = valore
                self.dOpz[nomeOpz.tag][1] = info

    def salvaFileOpzioni(self):
        oldFileConf = self.nomeFile+"_old_"+".xml"
        if os.path.isfile(oldFileConf):
          os.remove(oldFileConf)
        os.rename(self.nomeFile,oldFileConf)
        elConf = ET.Element('configurazione')
        
        dizOrdOpz = collections.OrderedDict(sorted(self.dOpz.items()))
        for nomeOpzione in dizOrdOpz:
            newPar = ET.SubElement(elConf,nomeOpzione)
            kVal = self.dOpz[nomeOpzione][0]
            if kVal == False :
               kVal = 'False'
            elif kVal == True :
               kVal = 'True'
            newPar.set("value",kVal)
            if len(self.dOpz[nomeOpzione])> 2:
                newPar.set("inf",self.dOpz[nomeOpzione][1])
        atree = ET.ElementTree(elConf) 
        atree.write(self.nomeFile)
