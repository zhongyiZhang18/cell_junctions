# -*- coding: utf-8 -*-
"""
Created on Wed May 24 15:01:17 2017

@author: roehl
"""
import numpy as np
import cv2
from skimage import morphology,segmentation,measure
from functools import partial
from scipy.spatial import distance as dist
import itertools
import matplotlib.pyplot as plt


#-------------------------Segmentation-----------------------------------------        
def RandomWalker(Edge,Markers):
    return segmentation.random_walker(Edge,Markers)
 
#--------------------------Improvements to segmentation------------------------        
def Improve_Segmentation(walker_segmentation,Cell_Size_Offset_From_Mean_In_Percent):
    '''
    Filter out the cells that intersect with the picture borders.
    Filter out the cells that are bigger than x percent of the mean cell size.
    Return improved segmented image. 
    '''
    
    #fuse all segements together that are at the picture borders
    left = walker_segmentation[:,0].ravel()
    right = walker_segmentation[:,-1].ravel()
    top = walker_segmentation[0].ravel()
    bottom = walker_segmentation[-1].ravel()
    frame = np.concatenate((left,right,top,bottom))
    frame = list(set(list(frame)))
    for element in frame:
        walker_segmentation[walker_segmentation == element] = 0

    # Get rid of all segments that are x percent bigger or smaller then the mean
    count = {}
    numbers = list(set(list(walker_segmentation.ravel())))
    numbers.sort() 
    for i in numbers[:-1]:
        count[i]= np.count_nonzero(walker_segmentation == i)
    count_mean = np.mean(list(count.values()))
    percentage_offset = count_mean*Cell_Size_Offset_From_Mean_In_Percent
    for key in count.keys():
        if count[key] < count_mean-percentage_offset or count[key] > count_mean+percentage_offset:
            walker_segmentation[walker_segmentation == key] = 0
    return walker_segmentation
        


#-------------------------------Prepare Image for mesurements------------------
def Segment_Image(Edge,Markers,Cell_Size_Offset_From_Mean_In_Percent):
    '''
    Prepare Images for messurement.
    
    Input:
        Markers = Markers from Nucli image for segmentation
        Edge = Edge image of Ecadherin image, created by machine learning edge creator
        
    Run segmntation and improvement of segmentation.
    Skeletonize and find boundarys of segmentation.
    Find junctions.
    Masked Image
    '''
    walker_segmentation = RandomWalker(Edge,Markers)
    walker_segmentation = Improve_Segmentation(walker_segmentation,Cell_Size_Offset_From_Mean_In_Percent)
    
    Segmented_cell_borders = segmentation.find_boundaries(walker_segmentation)
    Segmented_cell_borders = np.int8(Segmented_cell_borders)

    return Segmented_cell_borders,walker_segmentation
#%%
#--------------------------------find end of junction--------------------------

def sliding_window(self,img, stepSize, windowSize):
	# slide a window across the image
	for y in range(0, img.shape[0], stepSize):
		for x in range(0, img.shape[1], stepSize):
			# yield the current window
			yield (x, y, img[y:y + windowSize[1], x:x + windowSize[0]])

def extract3x3(self,img):
    winH = 3
    winW = 3
    patch = self.sliding_window(img,1,(winH,winW))
    Windows = []
    for (x,y,window) in patch:
        if window.shape[0] != winH or window.shape[1] != winW:
            continue
        else:
            Windows.append([x,y,window])
    return Windows
    
def FindEnds(self,CellCellBoarder):
    zeros = np.zeros((CellCellBoarder.shape[0]+2,CellCellBoarder.shape[1]+2))
    zeros[1:-1,1:-1]=CellCellBoarder
    cords = []
    windows = extract3x3(zeros)
    
    # All possible endings
    possible_ending = np.zeros((17,3,3))
    possible_ending[0] = np.array(((1,0,0),(0,1,0),(0,0,0)))
    possible_ending[1] = np.array(((0,1,0),(0,1,0),(0,0,0)))
    possible_ending[2] = np.array(((0,0,1),(0,1,0),(0,0,0)))
    possible_ending[3] = np.array(((0,0,0),(1,1,0),(0,0,0)))
    possible_ending[4] = np.array(((0,0,0),(0,1,1),(0,0,0)))
    possible_ending[5] = np.array(((0,0,0),(0,1,0),(1,0,0)))
    possible_ending[6] = np.array(((0,0,0),(0,1,0),(0,1,0)))
    possible_ending[7] = np.array(((0,0,0),(0,1,0),(0,0,1)))

    possible_ending[8] = np.array(((1,0,0),(1,1,0),(0,0,0)))
    possible_ending[9] = np.array(((1,1,0),(0,1,0),(0,0,0)))
    possible_ending[10] = np.array(((0,1,1),(0,1,0),(0,0,0)))
    possible_ending[11] = np.array(((0,0,1),(0,1,1),(0,0,0)))
    possible_ending[12] = np.array(((0,0,0),(0,1,1),(0,0,1)))
    possible_ending[13] = np.array(((0,0,0),(0,1,0),(0,1,1)))
    possible_ending[14] = np.array(((0,0,0),(0,1,0),(1,1,0)))
    possible_ending[15] = np.array(((0,0,0),(1,1,0),(1,0,0)))
    
    #possible_ending[16] = np.array(((0,0,0),(0,1,0),(0,0,0)))

    for element in windows:
        for x in range(16):
            if np.array_equal(element[2],possible_ending[x]):
                cords.append(element[:2])
    return cords
#-----------------------------------Improve corner Image for visualisation-----
def Improve_Corner_cords(self,cordinates,min_nucli_dist):
    Corner_combinations = list(itertools.combinations(cordinates, 2))
    for element in Corner_combinations:
        euclid = dist.euclidean(element[0],element[1])
        if euclid < min_nucli_dist:
            if element[1] in cordinates and element[0] in cordinates:
                cordinates.remove(element[1])
    return cordinates
#-------------------------------Collect Cell information-----------------------
def Cell_Analisis(Walker_Segmentation,Nucly_Cordinates):
    Cell_Propertys = measure.regionprops(Walker_Segmentation)
    Cells = {}
    
    for propertys in Cell_Propertys:
        idividual_propertys = {}
        idividual_propertys['Propertys'] = propertys
        
        idividual_propertys['AnalisedJunctions'] = {}
        idividual_propertys['AnalisedJunctions']['processedConnections'] = []
        
        binary1 = Walker_Segmentation == propertys.label
        idividual_propertys['BinaryImage'] = binary1
        binary2 = np.logical_xor(morphology.binary_dilation(binary1,morphology.square(3)),binary1)
        border = Walker_Segmentation * np.int8(binary2)
        set_of_border = list(set(border.ravel()))
        if 0 in set_of_border:
            set_of_border = set_of_border[1:]
        idividual_propertys['ConnectedCells'] = set_of_border
        
        idividual_propertys['Nucly'] = [[x_1,y_1] for x_1,y_1 in list(propertys.coords) for x_2,y_2 in Nucly_Cordinates if x_1 == x_2 and y_1 == y_2]
        Cells[propertys.label] = idividual_propertys
    
    return Cells
    
       