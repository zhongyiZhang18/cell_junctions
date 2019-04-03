# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 13:37:59 2018

@author: roehl
"""

from PyQt5.QtWidgets import QMainWindow,QWidget,QLineEdit,QLabel, QPushButton, QMessageBox,QHBoxLayout, QVBoxLayout,QComboBox,QLCDNumber, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator,QImage,QPixmap
#import ImageQt
from skimage.io import imread,imsave
import cv2
from scipy import misc
import numpy as np
from skimage import morphology
from sklearn.feature_extraction.image import extract_patches_2d
from Analise import Direct_Analisis

#%% Labels
class DirectAnalyse(QMainWindow):
    def __init__(self,parent=None,ImageName=None,GroundTruth=None,Labels=None):
        super(DirectAnalyse,self).__init__(parent)
        self.ParentLink = parent
        self.ImageName = ImageName
        self.GroundTruth = GroundTruth
        self.Labels = Labels
        self.initUI()

    def initUI(self):
        self.QuickKill = False
        self.CentralWindow = DirectAnalyseWindow(self)
        self.setCentralWidget(self.CentralWindow)
  
    def closeEvent(self, event):
        if self.QuickKill:
            event.accept()
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)
    
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
                
#%% Image Label Selection prior to trainig 
class DirectAnalyseWindow(QWidget):
    def __init__(self,parent=None):
        super(DirectAnalyseWindow,self).__init__(parent)
        self.ParentLink = parent
        self.Dilation = 1
        self.initUI()

    def initUI(self):  
        
        #
        self.LoadPatches()
        self.Create_Dilation_Overlay()
        #Dilation Pictures
        self.DilationPicture1 = QLabel()
        self.DilationPicture2 = QLabel()
        self.DilationPicture3 = QLabel()
        self.UpdateDilationPictures()
        
        hbox_Dilation = QHBoxLayout()
        hbox_Dilation.addWidget(self.DilationPicture1)
        hbox_Dilation.addWidget(self.DilationPicture2)
        hbox_Dilation.addWidget(self.DilationPicture3)

        LabelDilationAnalisis = QLabel('Dilation For Analisis')
        LcdDilationAnalisis = QLCDNumber(self)
        self.sldAnalisis = QSlider(Qt.Horizontal, self)       
            
        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox_Dilation)
        vbox1.addWidget(LabelDilationAnalisis)
        vbox1.addWidget(LcdDilationAnalisis)
        vbox1.addWidget(self.sldAnalisis)
        
        AnalyseButton = QPushButton("Analyse")
        AnalyseButton.clicked.connect(self.Analyse)
        
        
        hbox_Analyse = QHBoxLayout()
        hbox_Analyse.addStretch(1)
        hbox_Analyse.addWidget(AnalyseButton)

        vbox = QVBoxLayout()
        vbox.addLayout(vbox1)
        vbox.addLayout(hbox_Analyse)
        
        self.setLayout(vbox)
        

        #--------------------------------defaults------------------------------ 
        self.sldAnalisis.valueChanged.connect(self.LcdValueChanged)
        self.sldAnalisis.valueChanged.connect(LcdDilationAnalisis.display)
        self.sldAnalisis.setRange(1,10)
        self.sldAnalisis.setSliderPosition(1)

    def LcdValueChanged(self):
        self.Dilation = self.sldAnalisis.sliderPosition()
        self.Create_Dilation_Overlay()
        self.UpdateDilationPictures()

    
    def UpdateDilationPictures(self):
        self.DilationPicture1.setPixmap(QPixmap('Temp/DilationOverlay1.png'))
        self.DilationPicture2.setPixmap(QPixmap('Temp/DilationOverlay2.png'))
        self.DilationPicture3.setPixmap(QPixmap('Temp/DilationOverlay3.png'))
        
    def Analyse(self):
        Parameters = {}
        Parameters['Label1'] = self.ParentLink.Labels[0]
        Parameters['Label2'] = self.ParentLink.Labels[1]
        Parameters['Label3'] = self.ParentLink.Labels[2]
        Parameters['Cell_Size_Offset_From_Mean_In_Percent'] = 50
        Parameters['Analisis_Dilation'] = self.sldAnalisis.sliderPosition()
        Direct_Analisis(self.ParentLink.ImageName,self.ParentLink.GroundTruth,Parameters)
        self.ParentLink.QuickKill = True
        self.ParentLink.close()
    
    def LoadPatches(self):
        self.tmp_image = imread(self.ParentLink.ImageName)
        self.tmp_image = cv2.split(self.tmp_image)[self.ParentLink.Labels[0]]
        zeros = np.zeros(self.tmp_image.shape,dtype=self.tmp_image.dtype)
        groundtruth = self.ParentLink.GroundTruth[0][:,:].astype(self.tmp_image.dtype)
        tmp_data = cv2.merge((self.tmp_image,groundtruth,zeros))
        
        tmp_patches = extract_patches_2d(tmp_data,(int(self.tmp_image.shape[0]/8),int(self.tmp_image.shape[1]/8)),6)
        
        tmp_sum = []
        for x in range(6):
            tmp_sum.append((np.sum(tmp_patches[x,:,:,1]),x))
        selection = sorted(tmp_sum, reverse=True)[:3]
        
        self.Patches = []
        for element in selection:
            self.Patches.append((tmp_patches[element[1],:,:,0],np.uint8(tmp_patches[element[1],:,:,1])))
        
        
        
    def Create_Dilation_Overlay(self):
        for i,patch in enumerate(self.Patches):
            zeros = np.zeros(patch[0].shape,dtype='uint8')
            tmp_color = cv2.cvtColor(misc.bytescale(patch[0]),cv2.COLOR_GRAY2RGB)
            tmp_dialated_skeleton = morphology.dilation(patch[1],morphology.square(self.Dilation))
            overlay = cv2.merge((np.uint8(tmp_dialated_skeleton)*255,zeros,zeros))
            overlayed = cv2.addWeighted(tmp_color,1,overlay,1,0)        
            imsave('Temp/DilationOverlay{}.png'.format(i+1),overlayed)
      