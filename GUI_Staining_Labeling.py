# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:19:33 2018

@author: malte roehl
"""
from PyQt5.QtWidgets import QMainWindow,QWidget,QLabel, QPushButton, QMessageBox,QHBoxLayout, QVBoxLayout,QComboBox



#%% Labels
class StainingLabeling(QMainWindow):
    def __init__(self,parent=None):
        super(StainingLabeling,self).__init__(parent)
        self.ParentLink = parent
        self.initUI()

    def initUI(self):
        self.QuickKill = False
        self.CentralWindow = StainingLabelingWindow(self)
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
class StainingLabelingWindow(QWidget):
    def __init__(self,parent=None):
        super(StainingLabelingWindow,self).__init__(parent)
        self.ParentLink = parent
        self.initUI()

    def initUI(self):        
        
        LabelTrainingsIndex = QLabel('Selected Image:')
        self.ComboBoxTraining = QComboBox()
        for name in self.ParentLink.ParentLink.ImageNames   :
           self.ComboBoxTraining.addItem(name)
        
        LineEditTrainingsIndexBox = QHBoxLayout()
        LineEditTrainingsIndexBox.addWidget(LabelTrainingsIndex)
        LineEditTrainingsIndexBox.addWidget(self.ComboBoxTraining)        
            
        LabelHeadingLabels = QLabel('Staining:')
        
        labelLabel1 = QLabel('Label 1[Main Junctional]')
        self.ComboBoxLabel1 = QComboBox()
        self.ComboBoxLabel1.addItem('Channel 0(In a RGB = R)')
        self.ComboBoxLabel1.addItem('Channel 1(In a RGB = G)')
        self.ComboBoxLabel1.addItem('Channel 2(In a RGB = B)')
        self.ComboBoxLabel1.addItem('No Channel')
        self.ComboBoxLabel1.setToolTip('Label 1')
        vboxLabel1 = QVBoxLayout()
        vboxLabel1.addWidget(labelLabel1)
        vboxLabel1.addWidget(self.ComboBoxLabel1)
        
        labelLabel2 = QLabel('Label 2')
        self.ComboBoxLabel2 = QComboBox()
        self.ComboBoxLabel2.addItem('Channel 0(In a RGB = R)')
        self.ComboBoxLabel2.addItem('Channel 1(In a RGB = G)')
        self.ComboBoxLabel2.addItem('Channel 2(In a RGB = B)')
        self.ComboBoxLabel2.addItem('No Channel')
        self.ComboBoxLabel2.setToolTip('Label 2')
        vboxLabel2 = QVBoxLayout()
        vboxLabel2.addWidget(labelLabel2)
        vboxLabel2.addWidget(self.ComboBoxLabel2)
    
        labelLabel3 = QLabel('Label 3[Nuclei]')
        self.ComboBoxLabel3 = QComboBox()
        self.ComboBoxLabel3.addItem('Channel 0(In a RGB = R)')
        self.ComboBoxLabel3.addItem('Channel 1(In a RGB = G)')
        self.ComboBoxLabel3.addItem('Channel 2(In a RGB = B)')
        self.ComboBoxLabel3.addItem('No Channel')
        self.ComboBoxLabel3.setToolTip('Label 3')
        vboxLabel3 = QVBoxLayout()
        vboxLabel3.addWidget(labelLabel3)
        vboxLabel3.addWidget(self.ComboBoxLabel3)
        
        
        LineEditLabelBox = QHBoxLayout()
        LineEditLabelBox.addWidget(LabelHeadingLabels)
        LineEditLabelBox.addLayout(vboxLabel1)
        LineEditLabelBox.addLayout(vboxLabel2)
        LineEditLabelBox.addLayout(vboxLabel3)
        
        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.Save)
        
        hbox_save = QHBoxLayout()
        hbox_save.addStretch(1)
        hbox_save.addWidget(SaveButton)

        vbox = QVBoxLayout()
        vbox.addLayout(LineEditTrainingsIndexBox)
        vbox.addLayout(LineEditLabelBox)
        vbox.addLayout(hbox_save)
        
        self.setLayout(vbox)
        #--------------------------------defaults------------------------------ 
        self.ComboBoxLabel1.setCurrentIndex(0)
        self.ComboBoxLabel2.setCurrentIndex(1)
        self.ComboBoxLabel3.setCurrentIndex(2)
        self.Save()
        
    def Save(self):
        self.TrainingsImageName = self.ComboBoxTraining.currentText()
        self.Labels = (int(self.ComboBoxLabel1.currentIndex()),int(self.ComboBoxLabel2.currentIndex()),int(self.ComboBoxLabel3.currentIndex()))
        self.ParentLink.QuickKill = True
        self.ParentLink.close()