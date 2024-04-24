

import os
import time
import pickle
import sqlite3
import numpy as np
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout='wide')

if "ensaio_id" not in st.session_state:
    st.session_state.ensaio_id = None

sinais  = []

def conect_db():
    base_path = "C:/Users/lmest/Documents/projetos/ultrasoundMultiPlex/app/db/db"
    # conecta com o banco de dados
    conn = sqlite3.connect(base_path)
    return conn



con = conect_db()
cur = con.cursor()    
result_query = [
    list(row) for row in cur.execute(
        '''
        SELECT ensaios.id, descricao, sinal, data_criacao,observacao,indices_id,  parametro_tempo, parametro_canais, array_valores
        FROM ensaios  
        LEFT JOIN indices ON ensaios.indices_id = indices.id
        ORDER BY ensaios.id
        '''
    )
]


df = pd.DataFrame(
    result_query,
    columns=['id','Descrição', 'Sinal', 'Data de Criação', 'Observação','Indices_id', 'Tempo', 'Canais','array_valores'])

for row in df.iterrows():
    df.at[row[0],'array_valores'] = pickle.loads(row[1]['array_valores'])['array_dados']
    df.at[row[0],'Sinal'] = pickle.loads(row[1]['Sinal'])
    # verifica o menor array entre sinal e array_valores e diminui o maior para o tamanho do menor
    min_len = min(len(df.at[row[0],'Sinal']), len(df.at[row[0],'array_valores']))
    df.at[row[0],'Sinal'] = df.at[row[0],'Sinal'][:min_len]
    df.at[row[0],'array_valores'] = df.at[row[0],'array_valores'][:min_len]

    df.at[row[0],'ti'] = pickle.loads(row[1]['array_valores'])['ti']
    df.at[row[0],'tf'] = pickle.loads(row[1]['array_valores'])['tf']

df = df.explode(['Sinal','array_valores'])

# criar uma coluna de identificador chamada "descricao_tabela" contendo o nome do ensaio e o canal
df['descricao_tabela'] = df['Descrição'] + " - canal: " + df['array_valores'].apply(lambda x: str(x['valor']))
# df.reset_index(inplace=True)




with st.container():
    st.markdown("# Ensaios #")            
    gb = GridOptionsBuilder.from_dataframe(df[["descricao_tabela", "Data de Criação", "Observação"]])                        
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)            
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridOptions = gb.build()
    # time.sleep(0.5)
    data = AgGrid(df[['id','descricao_tabela', 'Sinal', 'Data de Criação', 'Observação','Indices_id', 'Tempo', 'Canais','array_valores']],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                #reload_data=True,
                fit_columns_on_grid_load=True)
    
    selected_rows = data["selected_rows"]
    # if selected_rows == None:
    #     selected_rows = []

    print(f'### SELECTED ROWS ### => {selected_rows}')
    st.markdown("##")
    graficos, informacoes = st.tabs(["Gráficos", "Informações sobre Ensaio"])
    with graficos:
        ensaios = []
        legenda = []
        dados = []            
        if (len(selected_rows) != 0):        
            # st.session_state.ensaio_id = selected_rows[0]['id']                
            # st.markdown(f":orange[{st.session_state.ensaio_id}]")                
            for select in selected_rows:
                ensaios.append(select['descricao_tabela'])
                sinais.append(select['Sinal'])
                legenda.append(select['descricao_tabela'])
            
            group_labels = [ensaios[:][:]]
            fig = make_subplots(rows=1, cols=1)

            for i in range (len(selected_rows)):
                if len(selected_rows) > 0:
                    fig.append_trace(go.Scatter(                        
                        y=sinais[i][:],name=group_labels[0][i]
                        ), row=1, col=1
                    )
            fig = fig.update_layout(showlegend=True)
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with informacoes:
            if (len(selected_rows) != 0):
                for select in selected_rows:
                    st.markdown("-----------------------------")
                    st.markdown("Ensaio: " + select['descricao_tabela'])
                    st.markdown("Quantidade de canais: " + str(select['Canais']))
                    st.markdown("Tempo em cada canal: "+ str(select["Tempo"]))
                    st.markdown("Data do ensaio: "+ pd.to_datetime(select["Data de Criação"]).strftime("%d/%m/%Y %H:%M:%S"))
                    st.markdown("Observação: "+select["Observação"])
