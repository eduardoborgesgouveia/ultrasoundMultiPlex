

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
        self.path_img = self.path_video.replace(self.pasta_img+".mkv", "img_"+self.pasta_img) + "\\"
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
        ret = []
        while success and i<max_signals:
            # time.sleep(0.1)
            vidcap.set(cv2.CAP_PROP_POS_FRAMES ,(frame_index + count))    # added this line time in miliseconds
            success,image = vidcap.read()
            print ('Read a new frame: ', success)
            if success:
                canal_folder =  pathOut + str(indices['array_dados'][i]['valor']) + "\\"
                if not os.path.exists(canal_folder):
                    os.makedirs(canal_folder)

                filename =  canal_folder + "frame" + str(count).zfill(4)+".jpg"
                cv2.imwrite(filename, image)     # save frame as JPEG file
                ob = {
                    "frame_index": count,
                    "path": filename,
                    "canal": indices['array_dados'][i]['valor']
                }
                ret.append(ob)

                count = int(count + (janela_tempo/1000*FRAMES_SEC))
                i = i + 1
            
        return ret


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
                if (img[i,j,0] > 190 and img[i,j,1] > 190 and img[i,j,2] < 170 ):
                    data_high[j] = i
                    last = i
                    break
                elif (img[i,j,0] > 120 and img[i,j,1] > 120 and img[i,j,2] < 90 ):
                    data_high[j] = i
                    last = i
                    break
                    
            for i in range(start, end)[::-1]:
                if (img[i,j,0] > 190 and img[i,j,1] > 190 and img[i,j,2] < 170 ):
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
            end = int(last+len(img)/2) if last != 0 else len(img)
            if end > len(img):
                end = len(img)
                        

            data[j] = len(img)-int(data_high[j]+data_low[j])/2

            
        data[0] = data[1] if data[0] == len(img) else data[0]
        for j in range(1, len(data)-1):
            if data[j] == len(img):
                if data[j] > data[j-1] and data[j] > data[j+1]:
                    data[j] = (data[j-1]+data[j+1])/2
        return data
    

    def convert(self):

        ret = self._extractImages(self.path_video, self.path_img, self.indices,self.tempo_sensor)
        data = []
        aux_data = []
        #listar todoas as pastas dentro da pasta pai
        for folders in os.listdir(self.path_img):
            # listar todos os arquivos da pasta
            path = self.path_img + folders
            aux_ob = {}
            for file in os.listdir(path):
                filename = os.fsdecode(file)
            
                signal = self._dataFromImage(self.path_img +folders+ "\\" +filename)
                aux_data.append(signal)
            
            #realiza a mediana dos sinais em aux_data e adiciona em data
            # aux_ob = {
            #     "sinal": np.median(aux_data, axis=0),
            #     "canal": folders
            # }
            data.append(np.median(aux_data, axis=0))
            aux_data = []


        return data


if __name__ == "__main__":
    path_video = "C:/Users/lmest/Videos/2024-04-24 14-59-38.mp4"
    indices = {'ti': 1713981578.5903769, 'tf': 1713981589.5911584, 'array_dados': [{'tempo': 1713981579.4068372, 'valor': 6}, {'tempo': 1713981580.4714148, 'valor': 7}, {'tempo': 1713981581.434758, 'valor': 8}, {'tempo': 1713981582.4608655, 'valor': 9}, {'tempo': 1713981583.4720786, 'valor': 10}, {'tempo': 1713981584.4472673, 'valor': 1}, {'tempo': 1713981585.4424858, 'valor': 2}, {'tempo': 1713981586.4539123, 'valor': 3}, {'tempo': 1713981587.454567, 'valor': 4}, {'tempo': 1713981588.433027, 'valor': 5}, {'tempo': 1713981589.428693, 'valor': 6}]}
    
    path = conversor(path_video,indices,1000).convert()