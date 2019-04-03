# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:22:06 2018

@author: roehl
"""
from PyQt5.QtWidgets import QMainWindow,QAction,QWidget,QLabel, QPushButton, QMessageBox,QHBoxLayout, QVBoxLayout,QLCDNumber, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import numpy as np
from skimage import morphology,filters
from skimage.io import imread,imsave
import os
import cv2
from GUI_Junctional_Image_Edit_Area import JunctionalImageEditArea
from GUI_Nuclei_Image_Edit_Area import NucleiImageEditArea
from Nucli_Detection import Find_Nuclei
import pickle

class CreateGroundTruthWidget(QMainWindow):
    def __init__(self,parent=None,ImageName=None,Labels=None):
        super(CreateGroundTruthWidget,self).__init__(parent)
        self.CreateImagesToWorkOn(ImageName,Labels)
        self.initUI()
        
    def initUI(self):
        #intital variables
        self.NucleiCordinates = None
        self.Rectangle = None
        self.CurrentEditArea = 'Junctional'
        self.QuickKill = False
        #for going back and forth
        self.EventListJunctional = []
        self.EventListNuclei = []
        self.CurrentEvent = -1
        
        #both plates
        self.JunctionMainWidget = JunctionalImageView(self)
        self.setCentralWidget(self.JunctionMainWidget)
        
        self.statusBar()
        self.ActivateBrush()
        self.LineWidth = 3
        
        self.AddNuclei()

        self.BrushAct = QAction(QIcon('GUI_Icons/paint-brush.png'), 'Brush', self)
        self.BrushAct.setShortcut('Ctrl+B')
        self.BrushAct.triggered.connect(self.ActivateBrush)

        self.LineAct = QAction(QIcon('GUI_Icons/ruler.png'), 'Line', self)
        self.LineAct.setShortcut('Ctrl+L')
        self.LineAct.triggered.connect(self.ActivateLine)
        
        self.RubberAct = QAction(QIcon('GUI_Icons/eraser.png'), 'Rubber', self)
        self.RubberAct.setShortcut('Ctrl+R')
        self.RubberAct.triggered.connect(self.ActivateRubber)
        
        self.SmallAct = QAction(QIcon('GUI_Icons/Small.png'), 'Smaller', self)
        self.SmallAct.setShortcut('Ctrl+S')
        self.SmallAct.triggered.connect(self.SmallerLineWidth)
        
        self.BigAct = QAction(QIcon('GUI_Icons/Big.png'), 'Bigger', self)
        self.BigAct.setShortcut('Ctrl+B')
        self.BigAct.triggered.connect(self.BiggerLineWidth)
    
        
        #Nucly based
        self.ChangeAct = QAction(QIcon('GUI_Icons/exchange.png'), 'Change', self)
        self.ChangeAct.triggered.connect(self.ChangeToNuclei)
        
        self.BackAct = QAction(QIcon('GUI_Icons/back.png'), 'Undo', self)
        self.BackAct.setShortcut('Ctrl+Z')
        self.BackAct.triggered.connect(self.Back)
        
        self.ForwardAct = QAction(QIcon('GUI_Icons/forward.png'), 'Redo', self)
        self.ForwardAct.setShortcut('Ctrl+F')
        self.ForwardAct.triggered.connect(self.Forward)  
        
        self.MoveNuclyAct = QAction(QIcon('GUI_Icons/grab.png'), 'Grab', self)
        self.MoveNuclyAct.setShortcut('Ctrl+M')
        self.MoveNuclyAct.triggered.connect(self.MoveNucly)
        self.MoveNuclyAct.setDisabled(True)
        
        self.CreateNuclyAct = QAction(QIcon('GUI_Icons/add.png'), 'Add', self)
        self.CreateNuclyAct.setShortcut('Ctrl+N')
        self.CreateNuclyAct.triggered.connect(self.AddNuclei)
        self.CreateNuclyAct.setDisabled(True)      
        
        self.toolbar = self.addToolBar('Painting')
        self.toolbar.addAction(self.BrushAct)
        self.toolbar.addAction(self.LineAct)
        self.toolbar.addAction(self.RubberAct)
        self.toolbar.addAction(self.SmallAct)
        self.toolbar.addAction(self.BigAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.ChangeAct)
        self.toolbar.addAction(self.BackAct)
        self.toolbar.addAction(self.ForwardAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.MoveNuclyAct)
        self.toolbar.addAction(self.CreateNuclyAct)
        
        
        self.setWindowTitle('Create Ground Truth')
        
    def ActivateBrush(self):
        self.Brush = True
        self.Line = False
        self.Rubber = False
        self.statusBar().showMessage('Brush')
    
    def ActivateLine(self):
        self.Brush = False
        self.Line = True
        self.Rubber = False
        self.statusBar().showMessage('Line')
        
    def ActivateRubber(self):
        self.Brush = False
        self.Line = False
        self.Rubber = True
        self.statusBar().showMessage('Rubber')
        
    def BiggerLineWidth(self):
        self.LineWidth += 1
    
    def SmallerLineWidth(self):
        if self.LineWidth > 1:
            self.LineWidth -= 1
        
    def Back(self):
        #To do
        pass
    
    def Forward(self):
        #To Do
        pass
    
    def MoveNucly(self):
        self.Add = False
        self.Move = True
        self.statusBar().showMessage('Move...Douple Click Removes')
    
    def AddNuclei(self):
        self.Add = True
        self.Move = False
        self.statusBar().showMessage('Add')
    
    def ChangeToNuclei(self):
        
        if self.CurrentEditArea == 'Junctional':
            self.BrushAct.setDisabled(True)
            self.LineAct.setDisabled(True)
            self.RubberAct.setDisabled(True)
            self.SmallAct.setDisabled(True)
            self.BigAct.setDisabled(True)
            self.MoveNuclyAct.setDisabled(False)
            self.CreateNuclyAct.setDisabled(False)
            
            
            self.NucleiMainWidget = NucleiImageView(self)
            self.setCentralWidget(self.NucleiMainWidget)
            self.NucleiMainWidget.NucleiImageEditArea.CreateNucleiMapRect(self.Rectangle)
            self.CurrentEditArea = 'Nuclei'
            
        elif self.CurrentEditArea == 'Nuclei':
            self.BrushAct.setDisabled(False)
            self.LineAct.setDisabled(False)
            self.RubberAct.setDisabled(False)
            self.SmallAct.setDisabled(False)
            self.BigAct.setDisabled(False)
            self.MoveNuclyAct.setDisabled(True)
            self.CreateNuclyAct.setDisabled(True) 
            
            self.NucleiCordinates,self.Rectangle = self.NucleiMainWidget.NucleiImageEditArea.MapNucleiLocation(self.OriginalJunctionalImage.shape)
            
            self.JunctionMainWidget = JunctionalImageView(self)
            self.setCentralWidget(self.JunctionMainWidget)
            self.CurrentEditArea = 'Junctional'

    
    def CreateImagesToWorkOn(self,ImageName,Labels):

        self.OriginalImageName = ImageName
        self.OriginalImage = imread(ImageName)
        
        #Junctional Image
        self.OriginalJunctionalImage = cv2.split(self.OriginalImage)[Labels[0]]# Main junctional label
        self.OverlayJunctionalImage = self.OriginalImage
        self.OverlayJunctionalImageName = 'Temp/tempJunctionalOverlay.png'
        imsave(self.OverlayJunctionalImageName,self.OverlayJunctionalImage)
        
        self.JunctionalPaintMap = np.zeros((self.OriginalJunctionalImage.shape))
        
        #Nucly Image
        if Labels[2] == 3:
            Labels[2] = 0
        self.OriginalNucleiImage = cv2.split(self.OriginalImage)[Labels[2]]# Main nuclei label
        self.OverlayNucleiImage = self.OriginalNucleiImage
        self.OverlayNucleiImageName = 'Temp/tempNucleiOverlay.png'
        imsave(self.OverlayNucleiImageName,self.OverlayNucleiImage)
        

    
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
            
    def Save(self):
        JunctionalGroundTruth = np.float32(self.JunctionalPaintMap)
        NucleiGroundTruth,Rect = self.NucleiMainWidget.NucleiImageEditArea.MapNucleiLocation(self.OriginalJunctionalImage.shape)
        Ground_Truth_Data = [JunctionalGroundTruth,NucleiGroundTruth]
        temp_name = os.path.join('Train files','{}.p'.format(os.path.basename(self.OriginalImageName.split('.')[0])))
        pickle.dump( Ground_Truth_Data, open( temp_name, "wb" ) )
        self.statusBar().showMessage('Saved')
        self.QuickKill = True
        self.close()


            
class NucleiImageView(QWidget):
    def __init__(self,parent=None):
        super(NucleiImageView,self).__init__(parent)
        self.ParentLink = parent
        self.initUI()
        
    def initUI(self):
        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.Save)
        
        ThresholdingButton = QPushButton("Thresholding")
        ThresholdingButton.clicked.connect(self.Threshold)

        hbox = QHBoxLayout()
        hbox.addWidget(SaveButton)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(ThresholdingButton)
        
        #Minimal Distance
        self.MinimalDistanceValue = 25
        self.labelMinimalDistance = QLabel('Minimal Distance:')
        self.lcdMinimalDistance = QLCDNumber(self)
        self.sldMinimalDistance = QSlider(Qt.Horizontal, self)
        self.sldMinimalDistance.valueChanged.connect(self.MinimalDistanceChangeSlider)
        self.sldMinimalDistance.valueChanged.connect(self.lcdMinimalDistance.display)
        self.sldMinimalDistance.setRange(1,100)
        self.sldMinimalDistance.setSliderPosition(25)
        
        vboxMinimalDistance = QVBoxLayout()
        hboxMinimalDistance = QHBoxLayout()
        hboxMinimalDistance.addWidget(self.labelMinimalDistance)
        hboxMinimalDistance.addWidget(self.lcdMinimalDistance)
        vboxMinimalDistance.addLayout(hboxMinimalDistance)
        vboxMinimalDistance.addWidget(self.sldMinimalDistance)
        
        #Small Groups
        self.SmallGroupsValue = 50
        self.labelSmallGroups = QLabel('Remove Small Groups:')
        self.lcdSmallGroups = QLCDNumber(self)
        self.sldSmallGroups = QSlider(Qt.Horizontal, self)
        self.sldSmallGroups.valueChanged.connect(self.SmallGroupsChangeSlider)
        self.sldSmallGroups.valueChanged.connect(self.lcdSmallGroups.display)
        self.sldSmallGroups.setRange(1,500)
        self.sldSmallGroups.setSliderPosition(50)
        
        vboxSmallGroups = QVBoxLayout()
        hboxSmallGroups = QHBoxLayout()
        hboxSmallGroups.addWidget(self.labelSmallGroups)
        hboxSmallGroups.addWidget(self.lcdSmallGroups)
        vboxSmallGroups.addLayout(hboxSmallGroups)
        vboxSmallGroups.addWidget(self.sldSmallGroups)        
        
        hbox3 = QHBoxLayout()
        hbox3.addLayout(hbox1)
        hbox3.addLayout(vboxMinimalDistance)
        hbox3.addLayout(vboxSmallGroups)
        hbox3.addLayout(hbox)
        
        self.NucleiImageEditArea = NucleiImageEditArea(self)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.NucleiImageEditArea)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        
    def Save(self):
        self.ParentLink.Save()

    def Threshold(self):
        Nuclei_Cordinates = Find_Nuclei(self.ParentLink.OriginalNucleiImage,self.SmallGroupsValue,self.MinimalDistanceValue)
        self.NucleiImageEditArea.clearAllExceptImage()
        self.NucleiImageEditArea.CreateNucleiMap(Nuclei_Cordinates)

    def MinimalDistanceChangeSlider(self):
        self.MinimalDistanceValue = self.sldMinimalDistance.value()
        
    def SmallGroupsChangeSlider(self):
        self.SmallGroupsValue = self.sldSmallGroups.value()
        
    
class JunctionalImageView(QWidget):

    def __init__(self,parent=None):
        super(JunctionalImageView,self).__init__(parent)
        self.ParentLink = parent
        self.initUI()
        
    def initUI(self):
        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.Save)
        
        ThresholdingButton = QPushButton("Thresholding")
        ThresholdingButton.clicked.connect(self.Threshold)

        DilatingButton = QPushButton("Dilating")
        DilatingButton.clicked.connect(self.Dilate)
        
        ErosionButton = QPushButton("Erosion")
        ErosionButton.clicked.connect(self.Erosion)

        SkeletonButton = QPushButton("Skeleton")
        SkeletonButton.clicked.connect(self.Skeleton)

        hbox = QHBoxLayout()
        hbox.addWidget(SaveButton)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(ThresholdingButton)
        hbox1.addWidget(DilatingButton)
        hbox1.addWidget(ErosionButton)
        hbox1.addWidget(SkeletonButton)
        
        hbox3 = QHBoxLayout()
        hbox3.addLayout(hbox1)
        hbox3.addLayout(hbox)
        
        self.JunctionalImageEditArea = JunctionalImageEditArea(self)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.JunctionalImageEditArea)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)
        self.JunctionalImageEditArea.OverlayImage()

        
    def Save(self):
        self.ParentLink.Save()
        
    def Threshold(self):
        self.JunctionalImageEditArea.clearAll()
        thres = filters.threshold_otsu(self.ParentLink.OriginalJunctionalImage)
        self.ParentLink.JunctionalPaintMap = self.ParentLink.OriginalJunctionalImage > thres
        self.ParentLink.JunctionalPaintMap = np.int8(self.ParentLink.JunctionalPaintMap)
        self.ParentLink.JunctionalPaintMap = morphology.remove_small_objects(np.bool8(self.ParentLink.JunctionalPaintMap),min_size=30,connectivity=2,in_place=True)# change this for changing threshold reduction method
        self.JunctionalImageEditArea.OverlayImage()
    
    def Dilate(self):
        self.JunctionalImageEditArea.clearAll()
        self.ParentLink.JunctionalPaintMap = morphology.dilation(self.ParentLink.JunctionalPaintMap,morphology.square(3))
        self.JunctionalImageEditArea.OverlayImage()
        
    def Erosion(self):
        self.JunctionalImageEditArea.clearAll()
        self.ParentLink.JunctionalPaintMap = morphology.erosion(self.ParentLink.JunctionalPaintMap,morphology.square(3))
        self.JunctionalImageEditArea.OverlayImage()
    
    def Skeleton(self):
        self.JunctionalImageEditArea.clearAll()
        self.ParentLink.JunctionalPaintMap = morphology.skeletonize(self.ParentLink.JunctionalPaintMap)
        self.ParentLink.JunctionalPaintMap = np.int8(self.ParentLink.JunctionalPaintMap)
        self.JunctionalImageEditArea.OverlayImage()