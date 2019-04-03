# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 18:03:56 2017

@author: roehl
"""
import numpy as np
from skimage import exposure
import matplotlib.pyplot as plt
import os
import pickle
import cv2
from scipy import misc
from skimage.io import imsave

def CheckFolder(Analisis_Name):
    temp_path = os.path.join('Results',Analisis_Name)
    if os.path.exists(temp_path):
        pass
    else:
        os.mkdir(temp_path)
        temp_path_QC = os.path.join(temp_path,'Quality_Control')
        temp_path_Results = os.path.join(temp_path,'Results')
        temp_path_Debug = os.path.join(temp_path_QC,'Debug')
        os.mkdir(temp_path_QC)
        os.mkdir(temp_path_Results)
        os.mkdir(temp_path_Debug)

def EdgeMap(NameForFiles,Edge_Map,ecad):
    edgepath = os.path.join(os.getcwd(),'Cell Segementation','Output',NameForFiles,'{}_Edge.png'.format(NameForFiles))
    ecadpath = os.path.join(os.getcwd(),'Cell Segementation','Output',NameForFiles,'{}_Ecad.tif'.format(NameForFiles))
    #save edge and ecad
    Edge_Detector.Save_Image_Programm(Edge_Map,edgepath)
    imsave(ecadpath,ecad)

def Nuclei(Analisis_Name,Label1,Label3,Nuclei_Cordinates, Markers):
    CheckFolder(Analisis_Name)
    
    #Save Python
    with open(os.path.join('Results',Analisis_Name,'Quality_Control','Debug','Nuclei_Cordinates.p'),'wb') as fn:
        pickle.dump(Nuclei_Cordinates,fn)

    Zeros = np.zeros(Label1.shape,dtype='uint8')
    Output_Label1 = cv2.cvtColor(misc.bytescale(Label1),cv2.COLOR_GRAY2RGB)
    Output_Label3 = cv2.cvtColor(misc.bytescale(exposure.equalize_hist(Label3)),cv2.COLOR_GRAY2RGB)
  
    Validation_Nuclei = np.copy(Zeros)
    for y,x in Nuclei_Cordinates:
        cv2.circle(Validation_Nuclei,(int(x),int(y)),5,255,5)
        
    Overlay_Nuclei = cv2.merge((np.uint8(Validation_Nuclei),Zeros,Zeros))   
    Overlayed_Nucli_Nucli = cv2.addWeighted(Output_Label3,0.5,Overlay_Nuclei,1,0)
    Overlayed_Nucli_Label1 = cv2.addWeighted(Output_Label1,1,Overlayed_Nucli_Nucli,1,0)
    Overlayed_Nucli_Nucli_Label1 = cv2.addWeighted(Output_Label1,1,Overlay_Nuclei,1,0)
    imsave(os.path.join('Results',Analisis_Name,'Quality_Control','Nuclei.png'),Overlayed_Nucli_Nucli)
    imsave(os.path.join('Results',Analisis_Name,'Quality_Control','Label1_Nuclei.png'),Overlayed_Nucli_Label1)
    imsave(os.path.join('Results',Analisis_Name,'Quality_Control','Label1_Nuclei_Nuclei.png'),Overlayed_Nucli_Nucli_Label1)
    
def Segmentation(Analisis_Name,Segmented_Cell_Borders, Walker_Segmentation):
    CheckFolder(Analisis_Name)
    #Save Python
    np.save(os.path.join('Results',Analisis_Name,'Quality_Control','Debug','Walker_Segmentation.npy'),Walker_Segmentation)
    plt.imsave(os.path.join('Results',Analisis_Name,'Quality_Control','Walker_Segmentation.png'),Walker_Segmentation,dpi=1200)
    
def MeasuredCells(Analisis_Name,Label1,Edge_Map,Cells):
    zeros = np.zeros(Edge_Map.shape,dtype='uint8')
    temp = zeros.copy()
    overlayEdge_Map = cv2.merge((np.uint8(Edge_Map)*255,zeros,zeros))
    output_Segmentation = cv2.cvtColor(misc.bytescale(Label1),cv2.COLOR_GRAY2RGB)
    for element in Cells.keys():
        center = Cells[element]['Propertys'].centroid
        cv2.putText(temp, str(element),(int(center[1]), int(center[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5,255)
    overlaySegmentation = cv2.merge((np.uint8(temp),zeros,zeros))
    
    overlayed_Segmentation = cv2.addWeighted(output_Segmentation,1,overlaySegmentation,1,0)
    overlayed_Segmentation = cv2.addWeighted(overlayed_Segmentation,1,overlayEdge_Map,1,0)
    
    imsave(os.path.join('Results',Analisis_Name,'Quality_Control','Segmented_Label1.png'),overlayed_Segmentation)
    
    with open(os.path.join('Results',Analisis_Name,'Quality_Control','Debug','Cells.p'),'wb') as fn:
        pickle.dump(Cells,fn)
        
'''
    #Overlay Images
    zeros = np.zeros(Segmented_cell_borders.shape,dtype='uint8')
    
    #create differnet output images
    output_ecad = cv2.cvtColor(misc.bytescale(ecad),cv2.COLOR_GRAY2RGB)
    
    
    
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
'''
