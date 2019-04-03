# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:20:37 2018

@author: roehl
"""
from PyQt5.QtWidgets import QMainWindow,QSplashScreen,QAction,QWidget,QLineEdit,QLabel,QGraphicsView,QGraphicsScene,QGraphicsLineItem, QPushButton,QLCDNumber, QSlider, QApplication, QFileDialog, QMessageBox, QDesktopWidget,QHBoxLayout, QVBoxLayout,QComboBox
from PyQt5.QtCore import Qt, QObject, QCoreApplication,QRectF,QPointF,QLineF, pyqtSignal, QT_VERSION_STR
from PyQt5.QtGui import QPainter,QPixmap,QPen,QImage,QPainterPath,QIcon,QIntValidator
#import ImageQt


#%% Parameter Mains
class ParametersAutomated(QMainWindow):
    def __init__(self,parent=None):
        super(ParametersAutomated,self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.QuickKill = False
        self.CentralWindow = ParametersAutomatedWindow(self)
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
                
#%% Parameter Selection 
class ParametersAutomatedWindow(QWidget):
    def __init__(self,parent=None):
        super(ParametersAutomatedWindow,self).__init__(parent)
        self.ParentLink = parent
        self.initUI()

    def initUI(self):        

        labelPatch = QLabel('Patch Size For Leanring')
        onlyInt = QIntValidator()
        self.LineEditPatch1 = QLineEdit()
        self.LineEditPatch1.setValidator(onlyInt)
        self.LineEditPatch2 = QLineEdit()
        self.LineEditPatch2.setValidator(onlyInt)
        LineEditPatchBox = QHBoxLayout()
        LineEditPatchBox.addWidget(self.LineEditPatch1)
        LineEditPatchBox.addWidget(self.LineEditPatch2)
        
        labelResize = QLabel('Resize Image For Learning')
        self.LineEditResize1 = QLineEdit()
        self.LineEditResize1.setValidator(onlyInt)
        self.LineEditResize2 = QLineEdit()
        self.LineEditResize2.setValidator(onlyInt)
        LineEditResizeBox = QHBoxLayout()
        LineEditResizeBox.addWidget(self.LineEditResize1)
        LineEditResizeBox.addWidget(self.LineEditResize2)
        
        labelAmountPatches = QLabel('Amount of Patches')
        lcdAmountPatches = QLCDNumber(self)
        self.sld = QSlider(Qt.Horizontal, self)
        
        labelDilationAnalisis = QLabel('Dilation For Analisis')
        lcdDilationAnalisis = QLCDNumber(self)
        self.sldAnalisis = QSlider(Qt.Horizontal, self)
        
        labelSmallObjectsRemove = QLabel('Remove Small Objects In Nucly Detection')
        lcdSmallObjectsRemove = QLCDNumber(self)
        self.sldSmallObjectsRemove = QSlider(Qt.Horizontal, self)
        
        labelNucliMinDist = QLabel('Minimal Distance Nucly')
        lcdNucliMinDist = QLCDNumber(self)
        self.sldNucliMinDist = QSlider(Qt.Horizontal, self)
        
        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.Save)
        
        QuitButton = QPushButton("Quit")
        QuitButton.clicked.connect(self.ParentLink.close)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(SaveButton)
        hbox.addWidget(QuitButton)
        
        vbox = QVBoxLayout()
        vbox.addWidget(labelResize)
        vbox.addLayout(LineEditResizeBox)
        vbox.addWidget(labelPatch)
        vbox.addLayout(LineEditPatchBox)
        vbox.addWidget(labelAmountPatches)
        vbox.addWidget(lcdAmountPatches)
        vbox.addWidget(self.sld)
        vbox.addWidget(labelDilationAnalisis)
        vbox.addWidget(lcdDilationAnalisis)
        vbox.addWidget(self.sldAnalisis)
        vbox.addWidget(labelSmallObjectsRemove)
        vbox.addWidget(lcdSmallObjectsRemove)
        vbox.addWidget(self.sldSmallObjectsRemove)
        vbox.addWidget(labelNucliMinDist)
        vbox.addWidget(lcdNucliMinDist)
        vbox.addWidget(self.sldNucliMinDist)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        
        #--------------------------------Slider setup-------------------------
        self.sld.valueChanged.connect(lcdAmountPatches.display)
        self.sld.setRange(1,10)
        self.sld.setSliderPosition(2)
        self.sldAnalisis.valueChanged.connect(lcdDilationAnalisis.display)
        self.sldAnalisis.setRange(0,50)
        self.sldAnalisis.setSliderPosition(0)
        self.sldSmallObjectsRemove.valueChanged.connect(lcdSmallObjectsRemove.display)
        self.sldSmallObjectsRemove.setRange(0,200)
        self.sldSmallObjectsRemove.setSliderPosition(5)
        self.sldNucliMinDist.valueChanged.connect(lcdNucliMinDist.display)
        self.sldNucliMinDist.setRange(0,100)
        self.sldNucliMinDist.setSliderPosition(20)
        #--------------------------------defaults------------------------------
        self.LineEditPatch1.setText('160')
        self.LineEditPatch2.setText('160')
        self.LineEditResize1.setText('640')
        self.LineEditResize2.setText('640')
        self.Save()
        
    def Save(self):
        self.parameters = {}
        self.parameters['Patch_Size'] = (int(self.LineEditPatch1.text()),int(self.LineEditPatch2.text()))
        self.parameters['Resize_Training'] = (int(self.LineEditResize1.text()),int(self.LineEditResize2.text())) 
        self.parameters['Amount_Patches'] = self.sld.sliderPosition()
        self.parameters['Dilation_Analisis'] = self.sldAnalisis.sliderPosition()
        self.parameters['Remove Small Objects In Nucly Detection'] = self.sldSmallObjectsRemove.sliderPosition()
        self.parameters['Minimal Distance Nucly'] = self.sldNucliMinDist.sliderPosition()
        self.ParentLink.QuickKill = True
        self.ParentLink.close()

        
