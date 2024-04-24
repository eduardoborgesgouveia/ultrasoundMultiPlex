

import os
import statistics
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import imageio
import cv2

class conversor():
    def __init__(self, _path_video,_indices,_tempo_sensor):
        self.path_video = _path_video.replace("/", "\\")
        self.pasta_img = self.path_video.split("\\")[-1].split(".")[0]
        self.path_img = self.path_video.replace(self.pasta_img+".mp4", "img_"+self.pasta_img) + "\\"
        self.indices = _indices
        self.tempo_sensor = _tempo_sensor

        if not os.path.exists(self.path_img):
            os.makedirs(self.path_img)
    
    def _extractImages(self, pathIn, pathOut, indices,janela_tempo):
        tempo_primeiro_indice = (indices['array_dados'][0]['tempo'] - indices['ti'])
        max_signals = len(indices['array_dados'])
        FRAMES_SEC = 30
        frame_index = int(tempo_primeiro_indice * FRAMES_SEC)
        count = 0
        vidcap = cv2.VideoCapture(pathIn)
        # success,image = vidcap.read()
        success = True
        i = 0
        while success and i<max_signals:
            # time.sleep(0.1)
            vidcap.set(cv2.CAP_PROP_POS_FRAMES ,(frame_index + count))    # added this line time in miliseconds
            success,image = vidcap.read()
            print ('Read a new frame: ', success)
            if success:
                cv2.imwrite( pathOut + "frame" + str(count).zfill(4)+".jpg", image)     # save frame as JPEG file
                count = int(count + (janela_tempo/1000*FRAMES_SEC))
                i = i + 1

    def _dataFromImage(self,imagePath):
        img = imageio.imread(imagePath)
        
        data_high = np.zeros(len(img[0]))
        data_low = np.zeros(len(img[0]))
        data = np.zeros(len(img[0]))
        start = 0
        end = len(img)
        last = 0
        mean = np.mean(img)
        std = np.std(img)
        for j in range(len(data)):
            for i in range(start, end):

                if (img[i,j,0] > 180 and img[i,j,1] > 180 and img[i,j,2] < 140 ):
                    data_high[j] = i
                    last = i
                    break
                elif (img[i,j,0] > 120 and img[i,j,1] > 120 and img[i,j,2] < 90 ):
                    data_high[j] = i
                    last = i
                    break
                    
            for i in range(start, end)[::-1]:
                if (img[i,j,0] > 180 and img[i,j,1] > 180 and img[i,j,2] < 140 ):
                    data_low[j] = i
                    last = int((last + i)/2)
                    break
                elif (img[i,j,0] > 120 and img[i,j,1] > 120 and img[i,j,2] < 90 ):
                    data_low[j] = i
                    last = int((last + i)/2)
                    break
                    
            start = int(last-len(img)/2)
            if start < 0:
                start = 0
            end = int(last+len(img)/2)
            if end > len(img):
                end = len(img)
                        

            data[j] = len(img)-int(data_high[j]+data_low[j])/2

            

        for j in range(1, len(data)-1):
            if data[j] == len(img):
                if data[j] > data[j-1] and data[j] > data[j+1]:
                    data[j] = (data[j-1]+data[j+1])/2
        return data
    
    def convert(self):

        self._extractImages(self.path_video, self.path_img, self.indices,self.tempo_sensor)
        data = []
        for file in os.listdir(self.path_img):
            filename = os.fsdecode(file)
            signal = self._dataFromImage(self.path_img +filename)
            data.append(signal)
        
        data = np.array(data)
        # mediana = np.zeros(len(data[0,:]))
        # for ii in range(len(data[0,:])):
        #     mediana[ii] = statistics.median(data[:,ii])

        return data


if __name__ == "__main__":
    path_video = "C:/Users/lmest/Videos/2024-04-23 11-31-25.mp4"
    indices = {'ti': 1713882685.801252, 'tf': 1713882696.801248, 'array_dados': [{'tempo': 1713882685.8560705, 'valor': 7}, {'tempo': 1713882686.98868, 'valor': 8}, {'tempo': 1713882687.9479873, 'valor': 9}, {'tempo': 1713882688.9720693, 'valor': 10}, {'tempo': 1713882689.9643524, 'valor': 1}, {'tempo': 1713882690.9241045, 'valor': 2}, {'tempo': 1713882691.979386, 'valor': 3}, {'tempo': 1713882692.9897125, 'valor': 4}, {'tempo': 1713882693.9341283, 'valor': 5}, {'tempo': 1713882694.9765882, 'valor': 6}, {'tempo': 1713882695.9538465, 'valor': 7}]}
    
    path = conversor(path_video,indices,1000).convert()