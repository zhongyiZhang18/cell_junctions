# -*- coding: utf-8 -*-
"""
Created on Wed May  3 10:05:48 2017

@author: roehl
"""
import numpy as np
import cv2
from sklearn.feature_extraction.image import extract_patches_2d
from skimage.io import imsave
from skimage import morphology
from sklearn.preprocessing import normalize
import scipy
import os
from sklearn.svm import SVC
from sklearn import preprocessing
import PIL
from random import randint
import matplotlib.pyplot as plt

class Maschine_Learning_Edge_Detection:
    
    def __init__(self,TrainigsData,Parameters):
        self.Original = TrainigsData[0]
        self.Skeleton = TrainigsData[1]
        
        #Resize if to big
        #self.Original = cv2.resize(self.Original,Parameters['Rezise_Training'])
        #self.Skeleton = cv2.resize(self.Skeleton,Parameters['Rezise_Training'])      #Nessasary??? 
        
        #Train Classifier
        self.Train_Classifier(Parameters)
        
#%% Training
    def Train_Classifier(self,Parameters):
        #Prepare Trainings Set by sclicing it in patches
        patched_original,patched_skeleton = self.Patch_Trainings_Data(Parameters)
        pre_processed_original,pre_processed_skeleton = self.Preprocess_Patches(patched_original,patched_skeleton,Parameters)
        
        #Calculate Features
        XFeature = self.FeatureExtract(pre_processed_original)
        XFeature = np.array(XFeature)
        XFeature = np.reshape(XFeature,(int(XFeature.shape[0]*XFeature.shape[1]),XFeature.shape[2]))
        
        pre_processed_skeleton = np.array(pre_processed_skeleton)
        YSkeleton = np.reshape(pre_processed_skeleton,(int(pre_processed_skeleton.shape[0]*pre_processed_skeleton.shape[1])))
        YSkeleton = np.array(YSkeleton).astype('int8')
        
        #XFeature,YSkeleton = self.BalanceClasses(XFeature,YSkeleton)
        XFeature = self.PreprocessFeatures(XFeature)
        
        svm = SVC()
        self.clf = svm.fit(XFeature,YSkeleton)
        
    def Patch_Trainings_Data(self,Parameters):
        max_patch = Parameters['Amount_Patches']
        patch_size = Parameters['Patch_Size']
        patched_original = extract_patches_2d(self.Original,patch_size,max_patch)
        patched_skeleton = extract_patches_2d(self.Skeleton,patch_size,max_patch)
        return patched_original,patched_skeleton

    def Preprocess_Patches(self,patched_original,patched_skeleton,Parameters):
        #sclice frame of skeleton >> because features have -1,-1 less on axis
        new_skeleton = []
        new_original = []
        for x in range(patched_original.shape[0]) :
            new_skeleton.append(patched_skeleton[x,1:Parameters['Patch_Size'][0]-1,1:Parameters['Patch_Size'][1]-1].ravel())
            new_original.append(np.array(patched_original[x,:,:]).astype('float32')) #possible normalize and data agumentation
        return new_original,new_skeleton
    

 
#%% Feature Extraction
    def FeatureExtract(self,Data):
        X_Feature = []
        for entry in Data:
            Windows = self.extract3x3(entry)
            FeaturedImage = []
            for element in Windows:
                intensity = self.intensity(element[2])
                Statistics = self.Statistics(element[2])
                OrientedDominaceField = self.OrientedDominaceField(element[2])
                combined = intensity + Statistics + OrientedDominaceField
                FeaturedImage.append(np.array(combined))
            X_Feature.append(np.array(FeaturedImage))
        return X_Feature
    
    def PreprocessFeatures(self,X_Features):
        temp = preprocessing.normalize(X_Features,axis=0)
        temp2 = preprocessing.scale(temp)
        return temp2
    
    def sliding_window(self,image, stepSize, windowSize):
    	# slide a window across the image
    	for y in range(0, image.shape[0], stepSize):
    		for x in range(0, image.shape[1], stepSize):
    			# yield the current window
    			yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

    def extract3x3(self,image):
        winH = 3
        winW = 3
        patch = self.sliding_window(image,1,(winH,winW))
        Windows = []
        for (x,y,window) in patch:
            if window.shape[0] != winH or window.shape[1] != winW:
                continue
            else:
                Windows.append([x,y,window])
        return Windows

        

        
    def FeatureExtractImage(self,Image):
        Windows = self.extract3x3(Image)
        FeaturedImage = []
        for element in Windows:
            intensity = self.intensity(element[2])
            Statistics = self.Statistics(element[2])
            OrientedDominaceField = self.OrientedDominaceField(element[2])
            combined = intensity + Statistics + OrientedDominaceField
            FeaturedImage.append(np.array(combined))
        return FeaturedImage    
#%% Features   
    def intensity(self,Window):
        Feature = Window.ravel()
        return list(Feature)
    
    def Statistics(self,Window):
        flat = Window.ravel()
        Median = np.median(flat)
        Range = np.ptp(flat)
        #Energy = 0
        SecondOrderMoment = scipy.stats.moment(flat,moment=2)
        ThirdOrderMoment = scipy.stats.moment(flat,moment=3)
        FourthOrderMoment = scipy.stats.moment(flat,moment=4)
        return [Median,Range,SecondOrderMoment,ThirdOrderMoment,FourthOrderMoment]#,Energy
    
    def OrientedDominaceField(self,Window):
        #not 100% sureabout this
        gx = cv2.Sobel(Window, cv2.CV_32F, 1, 0, ksize=1)
        gy = cv2.Sobel(Window, cv2.CV_32F, 0, 1, ksize=1)
        mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
        Feature = list(mag.ravel())+list(angle.ravel()) 
        return Feature

#------------------------------------------------------------------------------
#--------------------------Feature Extraction----------------------------------      

#------------------------------------------------------------------------------
    def BalanceClasses(self,XFeature,YSkeleton):
        newYSkeleton = []
        newXFeature = []
        count1 = np.count_nonzero(YSkeleton)
        count0 = len(YSkeleton)-count1
        if count0 < count1:
            diff = count0
            for x in range(len(YSkeleton)):
                if YSkeleton[x] == 1 and diff != 0:
                    newYSkeleton.append(YSkeleton[x])
                    newXFeature.append(XFeature[x])
                    diff -= 1
                elif YSkeleton[x] == 0:
                    newYSkeleton.append(YSkeleton[x])
                    newXFeature.append(XFeature[x])
                    
            return np.array(newXFeature),np.array(newYSkeleton)
            
        elif count0 > count1:
            diff = count1
            for x in range(len(YSkeleton)):
                if YSkeleton[x] == 0 and diff > 0:
                    newYSkeleton.append(YSkeleton[x])
                    newXFeature.append(XFeature[x])
                    diff -= 1
                elif YSkeleton[x] == 1:
                    newYSkeleton.append(YSkeleton[x])
                    newXFeature.append(XFeature[x])            
            return np.array(newXFeature),np.array(newYSkeleton)
            
        elif count0 == count1:
            return XFeature,YSkeleton

        
#-----------------------------------Classification-----------------------------      

#---------------------------Image Segmentation---------------------------------
    def Classify_Image(self,Image):
        #improve

        Image = np.array(Image).astype('float32')

        XFeature = self.FeatureExtractImage(Image)
        XFeature = np.array(list(XFeature))
        XFeature = self.PreprocessFeatures(XFeature)
        Predict = self.clf.predict(XFeature)
        Final[y+1:y+self.Patch_Size[0]-1,x+1:x+self.Patch_Size[1]-1]=self.Reconstruct_Image(Predict,self.Patch_Size)
        return Final
#------------------------------------------------------------------------------
#---------------------------Reconstruct----------------------------------------
    def Reconstruct_Image(self,Prediction,Shape):
        Rec = np.reshape(Prediction,(Shape[0]-2,Shape[1]-2))
        return Rec
#-------------------------------After Classifing-------------------------------------------

    def Post_Processing_Image(self,Image,selem=3,Iterations=1):
        selem = morphology.square(selem)
        temp = Image
        for x in range(0,Iterations):
            temp = morphology.binary_dilation(temp,selem)
            temp = morphology.skeletonize(temp)
        return temp
        
    def Final_Image(self,Image,Desired_Size):
        Image = np.float32(Image)
        resized = cv2.resize(Image,Desired_Size)
        return resized
        
    def Save_Image_Programm(self,Image,Path):
        Image = np.float32(Image)
        parent = os.path.dirname(Path)
        if not os.path.exists(parent):
            os.mkdir(parent)
        imsave(Path,Image)
    
        image_file = PIL.Image.open(Path) 
        image_file = image_file.convert('1') # convert image to black and white
        image_file.save(Path)
        return