# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 14:00:07 2017

@author: roehl
"""
import numpy as np
import os
import cv2
from skimage.io import imread
from skimage.color import rgb2gray
from HandleExel import HandleExel
from sklearn.feature_extraction import image
from sklearn.preprocessing import normalize
from skimage import morphology,feature,exposure,filters,measure
from scipy import ndimage as ndi
from scipy.spatial import distance as dist
import itertools
import matplotlib as plt
from sklearn.feature_extraction.image import extract_patches_2d

class Load_Data():
    
    def __init__(self):
        pass
    
    def is_number(self,var):
        try:
            if int(var):
                return True
        except Exception:
            return False
            
    def LoadfromsimpleExcel(self,path,chanel_ecad,chanel_nuc,From,To):
        final_data = []
        exel = HandleExel()
        work,tab = exel.Load(path,sheet='Test')
        data = exel.getValues(tab,'B{}'.format(From),'B{}'.format(To))
        label = exel.getValues(tab,'C{}'.format(From),'C{}'.format(To))
        for element in data:
            final_data.append(self.Load_Image(element,chanel_ecad,chanel_nuc)[0])
        
        return final_data,label,data
        
    def LoadfromExel(self,PathExel,PathImages,Exelfile,Sheets):
        exel = HandleExel()
        data,label,FeatureVector,FeatureVectorName = exel.LoadDataFromTable(PathExel,Exelfile,Sheets)
        
        newdata = []
        for element in data:
            temppath = os.path.join(PathImages,element)
            tempimage = imread(temppath, plugin='tifffile')
            tempimage = cv2.cvtColor(tempimage, cv2.COLOR_RGB2GRAY)
            newdata.append(np.array(tempimage))
        
        return np.array(newdata),label,FeatureVector,data,FeatureVectorName

    def LoadfromFolder(self,Path,Labels,Amount):
        for fn in os.listdir(Path):
            name = fn.split('_')
            if self.is_number(name[0]):
                plate_info = name[1].split('-')
                well_info = name[2]
                level_info = name[3]
            else:
                plate_info = name[0].split('-')
                well_info = name[1]
                level_info = name[2] 
                
    def loaddataset(self,Folder, Folderlist):
        '''
        Load the data from the selected Folder
        Data has to be formated like 'Experiment_Well_Label'
        Return is the data in a dictonary from data[welland experiment]={[label,image],[]...}
        '''
        data = {}
        temp = []
        for fn in os.listdir(Folder):
            if fn in Folderlist: 
                imagefolder = os.path.join(Folder,fn)
                for element in os.listdir(imagefolder):
                    imagepath = os.path.join(imagefolder,element)
                    
                    tempimage = imread(imagepath, plugin='tifffile')
                    tempimage = cv2.cvtColor(tempimage, cv2.COLOR_RGB2GRAY)
                    tempimage = normalize(tempimage, norm='l2', axis=1)
                    
                    temp.append(np.array(tempimage))
                data[fn] = np.array(temp)
                temp = []
        return data
        
#------------------------------------------------------------------------------
#--------------------------------Load Ecad-------------------------------------
    def Load_Image(self,Image_path,chanel_ecad,chanel_nuc):
        
        
        img = imread(Image_path, plugin='tifffile')

            
        img = cv2.split(img)
        ecad = np.float32(img[chanel_ecad])
        nuc = np.float32(img[chanel_nuc])

        return ecad,nuc

#------------------------------------------------------------------------------
#------------------------------Load Skeleton Trainings Data----------------------
    def Load_Trainings_Data_Skeleton(self,Folder_Train,Number_Images,Resize,Label_Dialation_prior):
        pathskeleton = os.path.join(Folder_Train,'Skeleton')
        pathoriginal = os.path.join(Folder_Train,'Original')
        
        skeleton_names = os.listdir(pathskeleton)
        original_names = os.listdir(pathoriginal)
        
        skeleton = [[x.split('.')[0],os.path.join(pathskeleton,x)] for i,x in enumerate(skeleton_names) if i < Number_Images]
        original = [[x.split('.')[0],os.path.join(pathoriginal,x)] for i,x in enumerate(original_names) if i < Number_Images]
        
        original = self.Load_Original(original,Resize)
        skeleton = self.Load_Skeleton(skeleton,Resize,Label_Dialation_prior)
        return original,skeleton 
        
    def Load_Skeleton(self,skeleton,Resize,Label_Dialation_prior):
        labels = []
        for element in skeleton:
            skel = imread(element[1])
            if Label_Dialation_prior > 0:
                skel = morphology.dilation(skel,morphology.square(2+Label_Dialation_prior))
            skel = cv2.resize(skel,Resize)
            thresh = 1
            binary = skel > thresh
            #binary = morphology.skeletonize(binary)
            labels.append(binary)
        return labels
    
    def Load_Original(self,original,Resize):
        data = []
        for element in original:
            ecad = imread(element[1], plugin='tifffile')
            ecad = cv2.resize(ecad,Resize)
            ecad = cv2.split(ecad)
            ecad = ecad[0]
            ecad_gray = ecad
            data.append(np.array(ecad_gray))
        return data
#--------------------------------------------------------------------------------
if __name__ == '__main__':
    Patch_Size = (100,75)
    Patch_Number = 1
    Number_Images = 1
    Patch_number_for_train = 1
    Rezise = (150,200)
    Label_Dialation_prior = 1
    blob_threshold = 0.15
    Image_Name = 'Test1'
    original_shape = (800,600)
    
    load = Load_Data()
   # morphology.dilation(,morphology.square(3))
    Image_path = r'C:\Users\roehl\Desktop\Deep_Dive_Test\DeepDive\Cell Segementation\Trainings_Data\Original\#5-5.tif'
    Image_path = r'C:\Users\roehl\Desktop\testactin.tif'
    
    ecad,nuc,nuc_blob,markers = load.Load_Image(Image_path,blob_threshold,original_shape,nucly_threshold=True)
    