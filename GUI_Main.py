# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 11:19:42 2017

@author: roehl
"""

import sys
from PyQt5.QtWidgets import QSplashScreen,QWidget, QPushButton, QApplication, QFileDialog, QMessageBox, QDesktopWidget,QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from time import sleep
import Analise
from GUI_Staining_Labeling import StainingLabeling
from GUI_Parameters_Automated import ParametersAutomated
from GUI_Create_GroundTruth import CreateGroundTruthWidget
from GUI_Direct_Analyse import DirectAnalyse
from GUI_Automated_Analyse import AutomatedAnalyse
import pickle
   
#%% Main Window
class MainWindow(QWidget):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.QuickKill = False
        
        self.SelectImagesButton = QPushButton("Select Images")
        self.SelectImagesButton.clicked.connect(self.OpenImages)
        
        self.SelectStainingButton = QPushButton("Select Staining")
        self.SelectStainingButton.clicked.connect(self.SelectStaining)
        self.SelectStainingButton.setDisabled(True)
        
        self.SelectGroundTruthButton = QPushButton("Select Ground Truth[Skeleton]")
        self.SelectGroundTruthButton.clicked.connect(self.OpenGroundTruth)
        self.SelectGroundTruthButton.setDisabled(True)
        
        self.CreateGroundTruthButton = QPushButton("Create Ground Truth[Skeleton]")
        self.CreateGroundTruthButton.clicked.connect(self.CreateGroundTruth)
        self.CreateGroundTruthButton.setDisabled(True)
        
        self.DirectAnalyseButton = QPushButton("Direct Analysis")
        self.DirectAnalyseButton.clicked.connect(self.DirectAnalysis)
        self.DirectAnalyseButton.setDisabled(True)
        
        self.AutomatedAnalyseButton = QPushButton("Automated Analyse")
        self.AutomatedAnalyseButton.clicked.connect(self.AutomatedAnalysis)
        self.AutomatedAnalyseButton.setDisabled(True)
        
        vbox_Analyse = QVBoxLayout()
        vbox_Analyse.addWidget(self.DirectAnalyseButton)
        vbox_Analyse.addWidget(self.AutomatedAnalyseButton)
        
        vbox_Ground_Truth = QVBoxLayout()
        vbox_Ground_Truth.addWidget(self.SelectGroundTruthButton)
        vbox_Ground_Truth.addWidget(self.CreateGroundTruthButton)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.SelectImagesButton)
        hbox.addWidget(self.SelectStainingButton)
        hbox.addLayout(vbox_Ground_Truth)
        hbox.addStretch(1)
        hbox.addLayout(vbox_Analyse)

        
        self.setLayout(hbox)
        
        self.resize(400, 200)
        self.center()
        self.setWindowTitle('Junction Analysis Program')   
        

        
    def OpenGroundTruth(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Ground Truth", "Train files","*.p", options=options)
        if fileName:
            self.GroundTruth = pickle.load( open( fileName, "rb" ) )
            #self.SetParametersAutomatedButtton.setDisabled(False)
            self.DirectAnalyseButton.setDisabled(False)
            
    def OpenImages(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"Select Images", "/","Tif Files (*.tif *.tiff);;All Files (*)", options=options)
        if files:
            self.ImageNames = files
            self.SelectStainingButton.setDisabled(False)

            
    def OpenParametersAutomated(self):
        self.ParametersAutomatedWidget = ParametersAutomated(self)
        self.ParametersAutomatedWidget.show()
        #self.AnalyseAutomatedButton.setDisabled(False) 
           
    def SelectStaining(self):
        self.StainingLabelingWidget = StainingLabeling(self)
        self.StainingLabelingWidget.show()
        self.SelectGroundTruthButton.setDisabled(False)
        self.CreateGroundTruthButton.setDisabled(False)

    def CreateGroundTruth(self):
        #create new png image to load !!
        labels = [self.StainingLabelingWidget.CentralWindow.Labels[0],self.StainingLabelingWidget.CentralWindow.Labels[1],self.StainingLabelingWidget.CentralWindow.Labels[2]]
        self.CreateGroundTruthWidget = CreateGroundTruthWidget(self,self.StainingLabelingWidget.CentralWindow.TrainingsImageName,labels)# to do better selection of images
        self.CreateGroundTruthWidget.show()
        
    def DirectAnalysis(self):
        self.DirectAnalyseWidget = DirectAnalyse(self,self.StainingLabelingWidget.CentralWindow.TrainingsImageName,self.GroundTruth,self.StainingLabelingWidget.CentralWindow.Labels)
        self.DirectAnalyseWidget.show()
    
    def AutomatedAnalysis(self):
        parameters = self.ParametersAutomatedWidget.CentralWindow.parameters
        parameters['Label1'] = self.StainingLabelingWidget.CentralWindow.Labels[0]
        parameters['Label2'] = self.StainingLabelingWidget.CentralWindow.Labels[1]
        parameters['Label3'] = self.StainingLabelingWidget.CentralWindow.Labels[2]
        Analise.Analsis(self.ImageNames,self.GroundTruthImages,parameters)
        self.QuickKill = True
        self.close()
        
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
            
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
    
def Wait():
    app = QApplication(sys.argv)
    splash_pix = QPixmap('myPic.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    sleep(10)
    splash.close()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

    


