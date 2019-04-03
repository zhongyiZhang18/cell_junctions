# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 09:11:12 2017

@author: roehl
"""
import numpy as np
from skimage import morphology,filters,measure
from scipy.spatial import distance as dist
import itertools

def Improve_Nucli(cordinates,min_nucli_dist):
    nucli_combinations = list(itertools.combinations(cordinates, 2))
    for element in nucli_combinations:
        euclid = dist.euclidean(element[0],element[1])
        if euclid < min_nucli_dist:
            if element[1] in cordinates and element[0] in cordinates:
                cordinates.remove(element[1])
    return cordinates
    

def Find_Nuclei(Label3,small_objects,min_nucli_dist):
    '''
    Function to detect the center of gravity in each cell nuclei and return their Cordinates and a 
    Marked image.
    '''
    #init Variables
    Cordinates = []
    #Threshold image 
    Thres = filters.threshold_otsu(Label3)# could develop better algorithm
    Binary = Label3 > Thres
    #remove small bright sports
    Without_Small_Objects = morphology.remove_small_objects(Binary,min_size=small_objects,connectivity=2)
    labeled_array, num_features = measure.label(np.int8(Without_Small_Objects),connectivity=2,return_num=True)

    regprops = measure.regionprops(labeled_array)
    for element in regprops:
        center = element.centroid
        Cordinates.append([int(center[0]),int(center[1])])
    Cordinates = Improve_Nucli(Cordinates,min_nucli_dist)
    return Cordinates

def CreateMarkers(NucleiCordinates,Imageshape):
    Markers = np.zeros(Imageshape)
    for x,y in NucleiCordinates:
        Markers[int(x),int(y)] = 1
    labeled_array = measure.label(np.int8(Markers),connectivity=2)
    return labeled_array


