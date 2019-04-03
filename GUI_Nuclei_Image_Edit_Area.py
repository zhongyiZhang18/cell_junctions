# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:21:33 2018

@author: roehl
"""
from PyQt5.QtWidgets import QGraphicsView,QGraphicsScene,QGraphicsLineItem,QGraphicsEllipseItem
from PyQt5.QtCore import Qt,QRectF,QPointF,QLineF,QPoint
from PyQt5.QtGui import QPainter,QPixmap,QPen,QImage,QPainterPath
#import ImageQt
import numpy as np
import cv2
from scipy import misc
from skimage.draw import line
from skimage import morphology
from skimage.io import imsave

#%% Image View    
class NucleiImageEditArea(QGraphicsView):
    def __init__(self,parent):
        QGraphicsView.__init__(self)
        self.ParentLink = parent
        self.initUI()
        
    def initUI(self):
        self.selected_item = None
        #zoom settings
        self.zommed = False
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.oldpos = (0,0)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self._pixmapHandle = None
        self.aspectRatioMode = Qt.KeepAspectRatio
        image = QImage(self.ParentLink.ParentLink.OverlayNucleiImageName)
        self.setImage(image)
        
        self.Paint = QPainterPath() 
        self.Pressed = False
        
        

    def wheelEvent(self, event):
        self.zommed = True
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        
        oldPos = self.mapToScene(event.pos())
        
        delta = event.angleDelta()
        if delta.y() < 0:
            factor = 1/1.25
        elif delta.y() > 0:
            factor = 1.25
        self.scale(factor,factor)
        
        newPos = self.mapToScene(event.pos())
        
        deltatrans = newPos - oldPos
        self.translate(deltatrans.x(), deltatrans.y())
        
    def clearAll(self):
        for element in self.scene.items():
            if element == self._pixmapHandle:
                self.clearImage()
            else:
                self.scene.removeItem(element)
                
    def clearAllExceptImage(self):
        for element in self.scene.items():
            if element == self._pixmapHandle:
                pass
            else:
                self.scene.removeItem(element)

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None
        
    def clearImage(self):
        """
        Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None
            
    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None
        
    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.imageshape = (pixmap.height(),pixmap.width())
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def updateViewer(self):
        if self.zommed:
            pass
        else:
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).
   
    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        if self.ParentLink.ParentLink.Move == True:
            item = self.itemAt(event.pos())
            if type(item) == QGraphicsEllipseItem:
                self.selected_item = item

    def mouseMoveEvent(self, event):
        if self.ParentLink.ParentLink.Move == True:
            if self.selected_item != None:
                point = self.mapToScene(event.pos())
                self.selected_item.setRect(QRectF(point.x(),point.y(),10,10))
        
            
    def mouseReleaseEvent(self, event):
        if self.ParentLink.ParentLink.Add == True:
            temp_pos = event.pos()
            x = int(temp_pos.x()-5)
            y = int(temp_pos.y()-5)
            point = self.mapToScene(QPoint(x,y))
            Round = QGraphicsEllipseItem(QRectF(point.x(),point.y(),10,10))
            pen = QPen(Qt.red, 10, Qt.SolidLine)
            Round.setPen(pen)
            self.scene.addItem(Round)  
        elif self.ParentLink.ParentLink.Move == True:
            if self.selected_item != None:
                point = self.mapToScene(event.pos())
                self.selected_item.setRect(QRectF(point.x(),point.y(),10,10))
                self.selected_item = None
                
    def mouseDoubleClickEvent(self, event):
            item = self.itemAt(event.pos())
            if type(item) == QGraphicsEllipseItem:
                self.scene.removeItem(item)
            

    def CreateNucleiMap(self,NucleiCordinates):
        if NucleiCordinates == None:
            pass
        else:
            for x,y in NucleiCordinates:
                point = QPoint(y,x)
                Round = QGraphicsEllipseItem(QRectF(point.x(),point.y(),10,10))
                pen = QPen(Qt.red, 10, Qt.SolidLine)
                Round.setPen(pen)
                self.scene.addItem(Round) 
              
    def CreateNucleiMapRect(self,Rectangle):
        if Rectangle == None:
            pass
        else:
            for element in Rectangle:
                Round = QGraphicsEllipseItem(element)
                pen = QPen(Qt.red, 10, Qt.SolidLine)
                Round.setPen(pen)
                self.scene.addItem(Round)  
    
       
    def MapNucleiLocation(self,ImageShape):
        NucleiCordinates = []
        Rectangle = []
        for element in self.scene.items():
            if element == self._pixmapHandle:
                pass
            elif type(element) == QGraphicsEllipseItem:
                Rectangle.append(element.rect())
                
                point = element.rect().center()
                x = point.y()
                y = point.x()
                if (0 <= x) and (x <= ImageShape[0]-1) and (0 <= y) and (y <= ImageShape[1]-1):
                    NucleiCordinates.append([int(x),int(y)])
        return NucleiCordinates, Rectangle