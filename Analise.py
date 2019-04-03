# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 14:02:39 2017

@author: roehl
"""
import Cell_Segmentation as Segment
from Machine_Learning_Edge_Detector_GUI import Maschine_Learning_Edge_Detection
from Cell_Measurement import Mesure_Cells
from HandleExel import SaveMeasurements
import Nucli_Detection
import QC_Functions as QC

import os
import numpy as np
import cv2
from skimage.io import imsave
import pickle

from skimage import morphology,exposure
from scipy import misc
from skimage.io import imread
import matplotlib.pyplot as plt

def Direct_Analisis(ImageName,GroundTruth,Parameters):

    #Load Image
    Img = imread(ImageName, plugin='tifffile')  
    Img = cv2.split(Img)
    #Allocate Lables
    Label1 = np.float32(Img[Parameters['Label1']])#Junction Marker 1
    Label2 = np.float32(Img[Parameters['Label2']])#Junction Marker 2
    Label3 = np.float32(Img[Parameters['Label3']])#Nucly Marker
    #Name of Output
    Analisis_Name = ImageName.split('/')[-1].split('.')[0]
    #Nucli Detection #better way
    Markers = Nucli_Detection.CreateMarkers(GroundTruth[1],Label3.shape)
    QC.Nuclei(Analisis_Name,Label1,Label3,GroundTruth[1], Markers)
    #Cell Segmentation
    Segmented_Cell_Borders, Walker_Segmentation = Segment.Segment_Image(GroundTruth[0],Markers,Parameters['Cell_Size_Offset_From_Mean_In_Percent'])
    QC.Segmentation(Analisis_Name,Segmented_Cell_Borders, Walker_Segmentation)
    Cells = Segment.Cell_Analisis(Walker_Segmentation,GroundTruth[1])
    Cells = Mesure_Cells(Label1,Label2,Cells,Parameters['Analisis_Dilation'])
    QC.MeasuredCells(Analisis_Name,Label1,Segmented_Cell_Borders,Cells)
    SaveMeasurements(Analisis_Name,Cells)
    

def Analsis(ImageNames,TrainingImages,Parameters):
    #%% Init Modules

    Edge_Detector = Maschine_Learning_Edge_Detection(TrainingImages,Parameters)
    segment = Cell_Segmentation()
    Cell_measure = Cell_Measurements()
    
    #%% Iterate Over Images
    for Name in ImageNames:
        # Loading of image
        img = imread(Name, plugin='tifffile')  
        img = cv2.split(img)
        
        Label1 = np.float32(img[Parameters['Label1']])
        Label2 = np.float32(img[Parameters['Label2']])
        Label3 = np.float32(img[Parameters['Label3']])  
        
        #Name of Output
        NameForFiles = Name.split('/')[-1].split('.')[0]
       
        #Nucli Detection
        nucli_cordinates, Markers = Nucli_Detection.Nucli_Tres(Label3,Parameters['small_objects'],Parameters['min_nucli_dist'])

        #Create Cell Boarder Map
        Edge_Map1 = Edge_Detector.Classify_Image(Label1)
        Edge_Map2 = Edge_Detector.Post_Processing_Image(Edge_Map1,Iterations=1)
        Edge_Map = Edge_Detector.Final_Image(Edge_Map2,(Label1.shape[1],Label1.shape[0]))

        #QC
        #Save Edge Image,Original Image(normalized),Nucli in ecad and nucli in Nuc
        QC.EdgeMap(NameForFiles,Edge_Map,Label1)


        #Cell Segmentation
        Segmented_cell_borders, walker_segmentation = segment.Segment_Image(Edge_Map,Markers,Parameters['Cell_Size_Offset_From_Mean_In_Percent'])
        Cell,Corner_Map,Corner_cords = segment.Cell_Analisis(walker_segmentation,nucli_cordinates)

        #Measure Cells
        Area_Perimeter,Internuclear_distance,Nucli_Offset,Junction_Linearity,Interface_Linearity,Coverage_index,Ecadherin_Intensity,Interface_Occupancy,Cluster_density = Cell_measure.Mesure_Cells(Label1,Cell,Analisis_Dilation)
        #----------------------------------------------------------------------
        
        #----------------------------------------------------------------------
        #plot for valiation purpose
        #Storage Path
        temp_path = os.path.join(os.getcwd(),'Cell Segementation','Output',NameForFiles)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
            
        #dilate like in analisis
        if Analisis_Dilation > 0:
            Segmented_cell_borders = morphology.binary_dilation(Segmented_cell_borders,morphology.square(Analisis_Dilation+2))
        
    
        #Overlay Images
        zeros = np.zeros(Segmented_cell_borders.shape,dtype='uint8')
        
        #create differnet output images
        output_ecad = cv2.cvtColor(misc.bytescale(ecad),cv2.COLOR_GRAY2RGB)
        output_Segmentation = cv2.cvtColor(misc.bytescale(Segmented_cell_borders),cv2.COLOR_GRAY2RGB)
        output_Nucli = cv2.cvtColor(misc.bytescale(exposure.equalize_hist(nuc)),cv2.COLOR_GRAY2RGB)
        
        #skeleton
        overlaySkel = cv2.merge((np.uint8(Segmented_cell_borders)*255,zeros,zeros))
        
        #corner
        overlayCorner = Corner_Map > 0
        overlayCorner = morphology.binary_dilation(overlayCorner,morphology.disk(4))
        overlayCorner = cv2.merge((np.uint8(overlayCorner)*255,zeros,zeros))
        
        #cell numbers
        temp_validation_segmentation = np.copy(zeros)
        for element in Cell.keys():
            center = Cell[element]['Center']
            cv2.putText(temp_validation_segmentation, str(element),(int(center[1]), int(center[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5,255)
        overlaySegmentation = cv2.merge((np.uint8(temp_validation_segmentation),zeros,zeros))
        
        #nucli
        temp_validation_nucli = np.copy(zeros)
        temp_validation_test_nuc = output_Nucli
        for y,x in nucli_cordinates:
            cv2.circle(temp_validation_nucli,(x,y),5,255,5)
        overlayNucli = cv2.merge((np.uint8(temp_validation_nucli),zeros,zeros))
        
        overlayed_ecad = cv2.addWeighted(output_ecad,1,overlaySkel,1,0)
        overlayed_Corner = cv2.addWeighted(output_ecad,1,overlayCorner,1,0)
        overlayed_Segmentation = cv2.addWeighted(output_Segmentation,1,overlaySegmentation,1,0)
        overlayed_Nucli_Nucli = cv2.addWeighted(output_Nucli,0.5,overlayNucli,1,0)
        overlayed_Nucli_ecad = cv2.addWeighted(output_ecad,1,overlayed_Nucli_Nucli,1,0)
        
        overlayed_Nucli_Nucli_ecad = cv2.addWeighted(output_ecad,1,overlayNucli,1,0)
        imsave(r'{}\Validation_Image_overlay.png'.format(temp_path),overlayed_ecad)
        imsave(r'{}\Validation_Image_overlay_Corner.png'.format(temp_path),overlayed_Corner)
        imsave(r'{}\Validation_Image_Segmentation.png'.format(temp_path),overlayed_Segmentation)
        imsave(r'{}\Validation_Image_Nucli_Nucli.png'.format(temp_path),overlayed_Nucli_Nucli)
        imsave(r'{}\Validation_Image_Nucli_Ecad.png'.format(temp_path),overlayed_Nucli_ecad)
        imsave(r'{}\Validation_Image_Nucli_Nucli_Ecad.png'.format(temp_path),overlayed_Nucli_Nucli_ecad)
        imsave(r'{}\Validation_walker_segmentation.png'.format(temp_path),walker_segmentation)
        #----------------------------------------------------------------------
        #--------------------------------Save Values In Excel--------------------------------------
        #exel = HandleExel()
        #exel.SaveCellMesurements(temp_path,Area_Perimeter,Internuclear_distance,Nucli_Offset,Junction_Linearity,Interface_Linearity,Coverage_index,Ecadherin_Intensity,Interface_Occupancy,Cluster_density)
        #----------------------------------------------------------------------   
if __name__=='__main__':
    ImageName = '#6-5.tif'
    path = 'Train files/#6-5.p'
    TrainingImages = pickle.load(open(path,'rb'))
    parameters = {}
    parameters['Label1'] = 0
    parameters['Label2'] = 1
    parameters['Label3'] = 2
    parameters['Rezise_Training'] = (640,640)
    parameters['Amount_Patches'] = 1
    parameters['Patch_Size'] = (160,160)
    parameters['small_objects'] = 5
    parameters['min_nucli_dist'] = 20
    parameters['Cell_Size_Offset_From_Mean_In_Percent'] = 50
    parameters['Analisis_Dilation'] = 2
    Direct_Analisis(ImageName,TrainingImages,parameters)