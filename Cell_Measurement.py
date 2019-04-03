# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 10:31:45 2017

@author: roehl
"""

import numpy as np
from skimage import morphology,measure,filters,segmentation
from scipy import ndimage as ndi
from scipy.spatial import distance as dist
import sys



#%%
def sliding_window(img, stepSize, windowSize):
	# slide a window across the image
	for y in range(0, img.shape[0], stepSize):
		for x in range(0, img.shape[1], stepSize):
			# yield the current window
			yield (x, y, img[y:y + windowSize[1], x:x + windowSize[0]])

def extract3x3(img):
    winH = 3
    winW = 3
    patch = sliding_window(img,1,(winH,winW))
    Windows = []
    for (x,y,window) in patch:
        if window.shape[0] != winH or window.shape[1] != winW:
            continue
        else:
            Windows.append([x,y,window])
    return Windows
    
def FindEnds(CellCellBoarder):
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
    
    possible_ending[16] = np.array(((0,0,0),(0,1,0),(0,0,0)))

    
    for element in windows:
        for x in range(17):
            if np.array_equal(element[2],possible_ending[x]):
                cords.append(element[:2])

           
    return cords
#%%
def Mesure_Cells(Label1,Label2,Cells,Analisis_Dilation=0):
    #calculate mesurements for every cell 

    for k in Cells.keys():
        #Area
        Cells[k]['Area'] = Cells[k]['Propertys'].area
        #Perimeter
        Cells[k]['Perimeter'] = Cells[k]['Propertys'].perimeter
        #Nucly Offset
        Cells[k]['NuclyOffset'] = dist.euclidean(Cells[k]['Nucly'][0],Cells[k]['Propertys'].local_centroid)#use centroid not of bounding box but of object!!!to do
        
        #Parameters Between Bordering Cells
        for o in Cells[k]['ConnectedCells']:
            #set all variables that will be used troughout the loop
            ConnectedCell = Cells[o]
            strConnectedCell = str(o)
            if strConnectedCell in Cells[k]['AnalisedJunctions']['processedConnections'] or str(k) in Cells[o]['AnalisedJunctions']['processedConnections']:
                pass
            else:
                #ceate Entry
                Cells[k]['AnalisedJunctions'][strConnectedCell] = {}
                Cells[k]['AnalisedJunctions']['processedConnections'].append(strConnectedCell)
                
                #Preparation of Basic structures to do the Analasis
                temp_binary_1 = morphology.binary_dilation(Cells[k]['BinaryImage'],morphology.square(3))
                temp_binary_2 = morphology.binary_dilation(ConnectedCell['BinaryImage'],morphology.square(3))
                Intersect = np.logical_and(temp_binary_1,temp_binary_2)
                Skeleton = morphology.skeletonize(Intersect)
                Cell_Cell_Boarder = np.int8(morphology.binary_dilation(Skeleton,morphology.square(Analisis_Dilation)))
                Cell_Cell_Boarder_Propertys = measure.regionprops(Cell_Cell_Boarder)[0]
                min_row, min_col, max_row, max_col = Cell_Cell_Boarder_Propertys.bbox
                Cell_Cell_Boarder_Ends = FindEnds(Skeleton[min_row:max_row,min_col:max_col])#chek if more than1
                Label1_ = Label1[min_row:max_row,min_col:max_col]
                Label2_ = Label2[min_row:max_row,min_col:max_col]
                Cell_Cell_Boarder_Label_1 = np.float32(np.int8(Cell_Cell_Boarder[min_row:max_row,min_col:max_col]))*Label1_
                Cell_Cell_Boarder_Label_2 = np.float32(np.int8(Cell_Cell_Boarder[min_row:max_row,min_col:max_col]))*Label2_
                
                Cells[k]['AnalisedJunctions'][strConnectedCell]['PredictedInterfaceLength'] = dist.euclidean(Cell_Cell_Boarder_Ends[0],Cell_Cell_Boarder_Ends[1])
                Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLength'] = np.sum(Skeleton[min_row:max_row,min_col:max_col])
                Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceArea'] = np.sum(Cell_Cell_Boarder[min_row:max_row,min_col:max_col])
                Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedInterfaceAreaIntensityLabel1'] = np.sum(Cell_Cell_Boarder_Label_1)
                Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedInterfaceAreaIntensityLabel2'] = np.sum(Cell_Cell_Boarder_Label_2)
                
                #use skeleton and dilate again so that junction end finding works without bugs
                #Individual Junctions Label1 #here we could implement a machine learning algorithm
                thres = filters.threshold_otsu(Cell_Cell_Boarder_Label_1)
                Single_Junctions_Binary = Cell_Cell_Boarder_Label_1 > thres
                Single_Junctions_Labeled = measure.label(Single_Junctions_Binary,connectivity=2)
                
                temp_labeled_junctions_results = {}
                list_all_endings = []
                for x in range(1,Single_Junctions_Labeled.max()+1,1):
                    temp_labeled_junctions_results[x] = {}
                    tempbinarysinglelabel = Single_Junctions_Labeled == x
                    
                    InduvidualJunctionLabel1 = np.float32(np.int8(tempbinarysinglelabel))*Label1_
                    InduvidualJunctionLabel2 = np.float32(np.int8(tempbinarysinglelabel))*Label2_
                    
                    skeleton_single_label = morphology.skeletonize(tempbinarysinglelabel)
                    
                    ends_of_labels = FindEnds(skeleton_single_label)
                    
                    for element in ends_of_labels:
                        list_all_endings.append(element)
                    
                    temp_labeled_junctions_results[x]['JunctionLength'] = np.sum(np.int8(skeleton_single_label))
                    temp_labeled_junctions_results[x]['JunctionArea'] = np.sum(np.int8(tempbinarysinglelabel))
                    temp_labeled_junctions_results[x]['JunctionIntensityLabel1'] = np.sum(np.int8(InduvidualJunctionLabel1))
                    temp_labeled_junctions_results[x]['JunctionIntensityLabel2'] = np.sum(np.int8(InduvidualJunctionLabel2))
                    if len(ends_of_labels) > 1:
                        temp_labeled_junctions_results[x]['JunctionEuclidianDistance'] = dist.euclidean(ends_of_labels[0],ends_of_labels[1])
                    else:
                        temp_labeled_junctions_results[x]['JunctionEuclidianDistance'] = None
                
                Junctions_Label_1 = np.float32(np.int8(Single_Junctions_Binary))*Label1_
                Junctions_Label_2 = np.float32(np.int8(Single_Junctions_Binary))*Label2_
                
                #find the closest junction towards the ends
                v = Cell_Cell_Boarder_Ends[0]
                v1 = Cell_Cell_Boarder_Ends[1]
                first_Ending = [dist.euclidean(u,v) for u in list_all_endings]
                first_Ending_min_index = np.argmin(first_Ending)
                second_Ending = [dist.euclidean(u,v1) for u in list_all_endings]
                second_Ending_min_index = np.argmin(second_Ending)
                
                
                
                Cells[k]['AnalisedJunctions'][strConnectedCell]['PredictedFragmentedJunctionLength'] = dist.euclidean(list_all_endings[first_Ending_min_index],list_all_endings[second_Ending_min_index])
                Cells[k]['AnalisedJunctions'][strConnectedCell]['FragmentedJunctionLength'] = np.sum(np.int8(morphology.skeletonize(Single_Junctions_Binary)))
                Cells[k]['AnalisedJunctions'][strConnectedCell]['JunctionProteinArea'] = np.sum(np.int8(Single_Junctions_Binary))
                Cells[k]['AnalisedJunctions'][strConnectedCell]['JunctionArea'] = None
                Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedJunctionAreaIntensityLabel1'] = np.sum(Junctions_Label_1)
                Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedJunctionAreaIntensityLabel2'] = np.sum(Junctions_Label_2)
                Cells[k]['AnalisedJunctions'][strConnectedCell]['IndividualJunctionPiecesResults'] = temp_labeled_junctions_results
                
                #Derived Measurements
                Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLinearityIndex'] = Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLength'] / Cells[k]['AnalisedJunctions'][strConnectedCell]['PredictedInterfaceLength']
                Cells[k]['AnalisedJunctions'][strConnectedCell]['CoverageIndex'] = Cells[k]['AnalisedJunctions'][strConnectedCell]['FragmentedJunctionLength'] / Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLength']
                Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceOccupancy'] = None#(Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLength'] / Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceArea'])*100
                Cells[k]['AnalisedJunctions'][strConnectedCell]['JunctionLabel1IntensityPerInterfaceArea'] = Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedJunctionAreaIntensityLabel1'] / Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceArea']
                Cells[k]['AnalisedJunctions'][strConnectedCell]['ClusterDensity'] = None#(Cells[k]['AnalisedJunctions'][strConnectedCell]['SummedJunctionAreaIntensityLabel1'] / Cells[k]['AnalisedJunctions'][strConnectedCell]['InterfaceLength'])*100
                
                
                #Internuclear Distance
                Cells[k]['AnalisedJunctions'][strConnectedCell]['Internuclear Distance'] = dist.euclidean(Cells[k]['Nucly'][0],ConnectedCell['Nucly'][0])
    return Cells
