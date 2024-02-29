# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 15:14:43 2022

@author: tulio
"""

import pandas as pd
import codecs
import imageio
import numpy as np
import matplotlib.pyplot as plt
import os

import sys
import argparse

import cv2
print(cv2.__version__)

def extractImages(pathIn, pathOut):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*500))    # added this line time in miliseconds
        success,image = vidcap.read()
        print ('Read a new frame: ', success)
        if success:
            cv2.imwrite( pathOut + "frame" + str(count).zfill(4)+".jpg", image)     # save frame as JPEG file
            count = count + 1

def dataFromImage(imagePath):


    img = imageio.imread(imagePath)
    
    data_high = np.zeros(len(img[0]))
    data_low = np.zeros(len(img[0]))
    data = np.zeros(len(img[0]))
    start = 0
    end = len(img)
    last = 0
    for j in range(len(data)):
        for i in range(start, end):
            if (img[i][j][0] > 180 and img[i][j][1] > 180 and img[i][j][2] < 140 ):
                data_high[j] = i
                last = i
                break
            elif (img[i][j][0] > 130 and img[i][j][1] > 130 and img[i][j][2] < 90 ):
                data_high[j] = i
                last = i
                break
            
                
        for i in range(start, end)[::-1]:
            if (img[i][j][0] > 180 and img[i][j][1] > 180 and img[i][j][2] < 140 ):
                data_low[j] = i
                last = int((last + i)/2)
                break
            elif (img[i][j][0] > 130 and img[i][j][1] > 130 and img[i][j][2] < 90 ):
                data_low[j] = i
                last = int((last + i)/2)
                break
                
        start = int(last-len(img)/4)
        if start < 0:
            start = 0
        end = int(last+len(img)/4)
        if end > len(img):
            end = len(img)
                    

        data[j] = len(img)-int(data_high[j]+data_low[j])/2
        

    for j in range(1, len(data)-1):
        if data[j] == len(img):
            if data[j] > data[j-1] and data[j] > data[j+1]:
                data[j] = (data[j-1]+data[j+1])/2
    return data

caminho = "C:\\Users\\Larissa\\OneDrive\\Larissa\\LMEst\\Ultrassom\\Ensaios com ultrassom\\transdutor colado\\"





path = "C:\\Users\\Larissa\\OneDrive\\Larissa\\LMEst\\Ultrassom\\Ensaios com ultrassom\\transdutor colado\\0-cola7\\"


# Check whether the specified path exists or not
isExist = os.path.exists(path)

if not isExist:
  
  # Create a new directory because it does not exist 
  os.makedirs(path)
 


extractImages(caminho+"0-cola7.mp4", caminho+"0-cola7\\")

data = []
for file in os.listdir(caminho+"0-cola7\\"):
    filename = os.fsdecode(file)
    signal = dataFromImage(caminho+"0-cola7\\" +filename)
    print ('Exctracting data from ', filename)
    data.append(signal)
    
np.save(caminho + "0-cola7", data)
#for i in range(len(data)):
 #   fig = plt.figure(figsize=(12.8, 7), dpi=100)
 
  #  plt.plot(np.arange(len(data[5])), data[i])
   # plt.title(i)
   # plt.show()
   # plt.pause  
    
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    