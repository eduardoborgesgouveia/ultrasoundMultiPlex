
from distutils.errors import DistutilsFileError
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statistics
import plotly.io as pio
pio.renderers.default='browser'

bbb=np.array(['baseline', 'cut 1', 'cut 2', 'cut 3', 'cut 4', 'cut 5', 'cut 6', 'cut 7', 'cut 8', 'cut 9'])
#bbb=np.array(['baseline', 'corte 1', 'corte 2', 'corte 3', 'corte 4', 'corte 5', 'corte 6', 'corte 7', 'corte 8', 'corte 9', 'corte 10', 'corte 11', 'corte 12', 'corte 13', 'corte 14', 'corte 15', 'corte 16', 'corte 17'])
#bbb=np.array(['corte 1'])
def retorna_plotagens(data,temp,condicao,offset):

    #comprimento = np.arange(len(data[0,:]))
    comprimento = np.linspace(0,145,len(data[0,:]))
    mediana = np.zeros(len(data[0,:]))
    for ii in range(len(data[0,:])):
        mediana[ii] = statistics.median(data[:,ii])

    if condicao == 1:

        if temp == 5:

            novo_comprimento = np.arange(offset,len(data[0,:])+offset,1)

            media_mediana.add_trace(go.Scatter(x = novo_comprimento, y = mediana,name = str(temp)+"°C"))

        else:

            media_mediana.add_trace(go.Scatter(x = comprimento, y = mediana,name = str(temp)+"°C"))

    else:

        media_mediana.add_trace(go.Scatter(x = comprimento, y = mediana,name = str(bbb[temp])))

    return media_mediana
       
if __name__ == '__main__':

    temperaturas = [0,1,2,3,4,5,6,7,8,9] # Quantidade de temperaturas para leitura
    



    # Importação dos dados:

    media_mediana = go.Figure()


    for ii in range(len(temperaturas)):

        data = np.load("C:\\Users\\Larissa\\OneDrive\\Larissa\\LMEst\\Ultrassom\\Ensaios com ultrassom\\Viga Bia\\2023\\Corte 1\\Normal\\Resultados\\0-p" + str(temperaturas[ii]) + ".npy")
     

    
       
        condicao = 0
        offset = 29
        media_mediana = retorna_plotagens(data,temperaturas[ii],condicao,offset)

    


    media_mediana.update_layout(title="Plotagem das medianas",xaxis_title="Posição (mm)",yaxis_title="dB (%)")
    media_mediana.show() 
    