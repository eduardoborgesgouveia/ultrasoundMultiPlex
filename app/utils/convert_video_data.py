

import os
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import imageio
import cv2

class conersor():
    def __init__(self, _path_video,_indices,_tempo_sensor):
        self.path_video = _path_video.replace("/", "\\")
        self.pasta_img = self.path_video.split("\\")[-1].split(".")[0]
        self.path_img = self.path_video.replace(self.pasta_img+".mp4", "img_"+self.pasta_img) + "\\"
        self.indices = _indices
        self.tempo_sensor = _tempo_sensor

        if not os.path.exists(self.path_img):
            os.makedirs(self.path_img)
    
    def _extractImages(pathIn, pathOut, indices,janela_tempo):
        tempo_primeiro_indice = (indices['array_dados'][0]['tempo'] - indices['ti'])*1000
        count = 0
        vidcap = cv2.VideoCapture(pathIn)
        success,image = vidcap.read()
        success = True
        while success:
            vidcap.set(cv2.CAP_PROP_POS_MSEC,(tempo_primeiro_indice + count))    # added this line time in miliseconds
            success,image = vidcap.read()
            print ('Read a new frame: ', success)
            if success:
                cv2.imwrite( pathOut + "frame" + str(count).zfill(4)+".jpg", image)     # save frame as JPEG file
                count = count + janela_tempo

    def _dataFromImage(imagePath):
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
    
    def convert(self):

        conersor._extractImages(self.path_video, self.path_img, self.indices,self.tempo_sensor)
        data = []
        for file in os.listdir(self.path_img):
            filename = os.fsdecode(file)
            signal = conersor._dataFromImage(self.path_img +filename)
            data.append(signal)
        
        data = np.array(data)
        # mediana = np.zeros(len(data[0,:]))
        # for ii in range(len(data[0,:])):
        #     mediana[ii] = statistics.median(data[:,ii])

        return data



        