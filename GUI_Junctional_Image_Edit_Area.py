# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:21:33 2018

@author: roehl
"""
from PyQt5.QtWidgets import QGraphicsView,QGraphicsScene,QGraphicsLineItem
from PyQt5.QtCore import Qt,QRectF,QPointF,QLineF
from PyQt5.QtGui import QPainter,QPixmap,QPen,QImage,QPainterPath
#import ImageQt
import numpy as np
import cv2
from scipy import misc
from skimage.draw import line
from skimage import morphology
from skimage.io import imsave

#%% Image View    
class JunctionalImageEditArea(QGraphicsView):
    def __init__(self,parent):
        QGraphicsView.__init__(self)
        self.ParentLink = parent
        self.initUI()
        
    def initUI(self):
        self.zommed = False
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.oldpos = (0,0)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self._pixmapHandle = None
        self.aspectRatioMode = Qt.KeepAspectRatio
        image = QImage(self.ParentLink.ParentLink.OverlayJunctionalImageName)
        self.setImage(image)
        
        self.Paint = QPainterPath() 
        self.Pressed = False
        
        self.OverlayImage()

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
        self.Pressed = True
        self.startpoint = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event):
        locationtest = self.mapToScene(event.pos())
        locationtest = True if 0 <= locationtest.y() <= self.imageshape[0] and 0 <= locationtest.x() <= self.imageshape[1] else False
        if self.ParentLink.ParentLink.Brush == True and self.Pressed == True and locationtest :
            start = QPointF(self.startpoint)
            end = QPointF(self.mapToScene(event.pos()))
            Line = QGraphicsLineItem(QLineF(start, end))
            pen = QPen(Qt.red, self.ParentLink.ParentLink.LineWidth, Qt.SolidLine)
            Line.setPen(pen)
            self.scene.addItem(Line)
            self.startpoint = self.mapToScene(event.pos())
            #improve
            self.ParentLink.ParentLink.JunctionalPaintMap[int(self.startpoint.y()-self.ParentLink.ParentLink.LineWidth):int(self.startpoint.y()+self.ParentLink.ParentLink.LineWidth),int(self.startpoint.x()-self.ParentLink.ParentLink.LineWidth):int(self.startpoint.x()+self.ParentLink.ParentLink.LineWidth)] = 1
            
        if self.ParentLink.ParentLink.Rubber == True and self.Pressed == True and locationtest:
            start = QPointF(self.startpoint)
            end = QPointF(self.mapToScene(event.pos()))
            Line = QGraphicsLineItem(QLineF(start, end))
            pen = QPen(Qt.blue, self.ParentLink.ParentLink.LineWidth, Qt.SolidLine)
            Line.setPen(pen)
            self.scene.addItem(Line)
            self.startpoint = self.mapToScene(event.pos())
            self.ParentLink.ParentLink.JunctionalPaintMap[int(self.startpoint.y()-self.ParentLink.ParentLink.LineWidth):int(self.startpoint.y()+self.ParentLink.ParentLink.LineWidth),int(self.startpoint.x()-self.ParentLink.ParentLink.LineWidth):int(self.startpoint.x()+self.ParentLink.ParentLink.LineWidth)] = 0
        if self.ParentLink.ParentLink.Line == True and self.Pressed == True and locationtest:
            self.clearAllExceptImage()
            start = QPointF(self.startpoint)
            end = QPointF(self.mapToScene(event.pos()))
            Line = QGraphicsLineItem(QLineF(start, end))
            pen = QPen(Qt.red, self.ParentLink.ParentLink.LineWidth, Qt.SolidLine)
            Line.setPen(pen)
            self.scene.addItem(Line)
            
            
    def mouseReleaseEvent(self, event):
        self.Pressed = False
        locationtest1 = self.mapToScene(event.pos())
        locationtest1 = True if 0 <= locationtest1.y() <= self.imageshape[0] and 0 <= locationtest1.x() <= self.imageshape[1] else False
        locationtest2 = self.startpoint
        locationtest2 = True if 0 <= locationtest2.y() <= self.imageshape[0] and 0 <= locationtest2.x() <= self.imageshape[1] else False
        if self.ParentLink.ParentLink.Line == True and locationtest1 and locationtest2:
            start = self.startpoint
            end = self.mapToScene(event.pos())
            Line = QGraphicsLineItem(QLineF(start, end))
            pen = QPen(Qt.red, self.ParentLink.ParentLink.LineWidth, Qt.SolidLine)
            Line.setPen(pen)
            self.scene.addItem(Line)
            zeros = np.zeros(self.ParentLink.ParentLink.JunctionalPaintMap.shape,dtype=int)
            rr,cc = line(int(start.y()),int(start.x()),int(end.y()),int(end.x()))
            zeros[rr,cc] = 1
            if self.ParentLink.ParentLink.LineWidth == 1:
                self.ParentLink.ParentLink.JunctionalPaintMap[rr,cc] = 1
            else:
                zeros = morphology.binary_dilation(zeros,morphology.square(self.ParentLink.ParentLink.LineWidth))
                zeros = np.int8(zeros)
                rr,cc = np.nonzero(zeros)
                self.ParentLink.ParentLink.JunctionalPaintMap[rr,cc] = 1

        self.OverlayImage()
            
    def OverlayImage(self):
        zeros = np.zeros(self.ParentLink.ParentLink.JunctionalPaintMap.shape,dtype='uint8')
        tempimg = self.ParentLink.ParentLink.OriginalJunctionalImage
        output_color = cv2.cvtColor(misc.bytescale(tempimg),cv2.COLOR_GRAY2RGB)
        overlay = cv2.merge((np.uint8(self.ParentLink.ParentLink.JunctionalPaintMap)*255,zeros,zeros))
        overlayed = cv2.addWeighted(output_color,1,overlay,1,0)
        imsave(self.ParentLink.ParentLink.OverlayJunctionalImageName,overlayed)
        self.clearImage()
        image = QImage(self.ParentLink.ParentLink.OverlayJunctionalImageName)
        self.setImage(image)