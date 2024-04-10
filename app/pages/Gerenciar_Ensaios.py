


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

# TODO: alterar o nome para sinais
forcas  = []

def conect_db():
    # conecta com o banco de dados
    conn = sqlite3.connect("./app/db/db")
    return conn


def get_sinal(df,id):
    sinal = pickle.loads(df[df['id'] == id]['Sinal'][df[df['id'] == id]['Sinal'].index[0]])
    return sinal

def get_indices():
    con = conect_db()
    cur = con.cursor()    
    result_query = [
        list(row) for row in cur.execute(
            '''
            SELECT id, parametro_tempo, parametro_canais, array_valores FROM indices  ORDER BY id
            '''
        )
    ]

    df = pd.DataFrame(
        result_query,
        columns=['id','Tempo', 'Canais','array_valores'])
    return df

con = conect_db()
cur = con.cursor()    
result_query = [
    list(row) for row in cur.execute(
        '''
        SELECT id, descricao, sinal, data_criacao,observacao,indices_id FROM ensaios  ORDER BY id
        '''
    )
]

df = pd.DataFrame(
    result_query,
    columns=['id','Descrição', 'Sinal', 'Data de Criação', 'Observação','Indices_id'])

with st.container():
    st.markdown("# Ensaios #")            
    gb = GridOptionsBuilder.from_dataframe(df[["Descrição", "Data de Criação", "Observação"]])                        
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)            
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridOptions = gb.build()

    data = AgGrid(df[['id','Descrição', 'Data de Criação', 'Observação']],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                #reload_data=True,
                fit_columns_on_grid_load=True)

    selected_rows = data["selected_rows"]
    print(f'### SELECTED ROWS ### => {selected_rows}')

    graficos, informacoes = st.tabs(["Gráficos", "Informações sobre Ensaio"])
    with graficos:
        ensaios = []
        legenda = []
        dados = []            
        if (len(selected_rows) != 0):        
            st.session_state.ensaio_id = selected_rows[0]['id']                
            st.markdown(f":orange[{st.session_state.ensaio_id}]")                
            for select in selected_rows:
                ensaios.append(select['Descrição'])
                forcas.append(get_sinal(df,select['id']))
                legenda.append(select['Descrição'])
            
            group_labels = [ensaios[:][:]]
            fig = make_subplots(rows=10, cols=1)
            #TODO: ver como organizar os gráficos

            for i in range (len(selected_rows)):
                if len(selected_rows) > 0:
                    for j in forcas[i]:
                        fig.append_trace(go.Scatter(                        
                            y=j,name=group_labels[0][i]
                            ), row=1, col=1
                        )
            fig = fig.update_layout(showlegend=True)
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        #TODO: adicionar as infos do ensaio
        with informacoes:
            st.header("A dog")
            df_indices = get_indices()
            for select in selected_rows:
                indice_id = df.loc[df['id'] == select['id'],'Indices_id'].values[0]
                array_selected = pickle.loads(df_indices[df_indices['id'] == indice_id]['array_valores'][df_indices[df_indices['id'] == indice_id]['array_valores'].index[0]])
                st.text(array_selected)
            st.image("https://static.streamlit.io/examples/dog.jpg", width=200)