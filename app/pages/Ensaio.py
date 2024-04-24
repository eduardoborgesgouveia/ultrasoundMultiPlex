from datetime import datetime
import os
import pickle
import sqlite3
import time
import streamlit as st
import numpy as np
import obsws_python as obs
from utils.convert_video_data import conversor


st.set_page_config(layout='wide')


if "recording" not in st.session_state:
    st.session_state.recording = False

if "nome_ensaio" not in st.session_state:
    st.session_state.nome_ensaio = ""
if "db_connection" not in st.session_state:
    st.session_state.db_connection = None
if "multiplex_indices_time" not in st.session_state:
    st.session_state.multiplex_indices_time = []
if "array_dados_indices" not in st.session_state:
    st.session_state.array_dados_indices = None
if "status_conexao_obs" not in st.session_state:
    st.session_state.status_conexao_obs = False
if "observacao" not in st.session_state:
    st.session_state.observacao = "Sem observação"
if "connection_status" not in st.session_state:
    st.session_state.connection_status = None
if "conexao_obs" not in st.session_state:
    st.session_state.conexao_obs = None


## conexão db para salvar os dados
## banco sqlite armazenado em db/db.sqlite
def conect_db():
    base_path = "C:/Users/lmest/Documents/projetos/ultrasoundMultiPlex/app/db/db"
    # conecta com o banco de dados
    conn = sqlite3.connect(base_path)
    return conn

def inserir_indice():
    # pegar os dados do data_multiplex_received_queue que estejam entre os tempos de inicio e fim do multiplex_indices_time
    ob_ind = st.session_state.array_dados_indices
    ob_axu = {
        "parametro_tempo": st.session_state.tempo_sensor,
        "parametro_canais": st.session_state.quantidade_sensor,
        "array_dados": pickle.dumps(ob_ind)
    }
    st.session_state.multiplex_indices_time = []
    conn = conect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
                        f"INSERT INTO indices (parametro_tempo, parametro_canais, array_valores) VALUES (?, ?, ?)",
                        (
                            ob_axu["parametro_tempo"],
                            ob_axu["parametro_canais"],
                            ob_axu["array_dados"],
                        ),
                    )
        conn.commit()
        return True, cursor.lastrowid
    except Exception as e:
        print(e)
        conn.rollback()
        return False,None
    
def inserir_ensaio(descricao, id_indice, caminho_arquivo, sinal, observacao):
    conn = conect_db()
    cursor = conn.cursor()
    # TODO: fazer verificações
    ob_aux = {
        "caminho_arquivo": caminho_arquivo,
        "sinal": pickle.dumps(sinal),
        "observacao": observacao,
        "data_criacao": datetime.now(),
        "descricao": descricao if descricao else "Sem descrição",
        "id_indice": id_indice
    }

    try:
        cursor.execute(
                        f"INSERT INTO ensaios (descricao, indices_id, caminho_arquivo, sinal, data_criacao, observacao) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            ob_aux["descricao"],
                            ob_aux["id_indice"],
                            ob_aux["caminho_arquivo"],
                            ob_aux["sinal"],
                            ob_aux["data_criacao"],
                            ob_aux["observacao"],
                        ),
                    )
        conn.commit()
        return True, cursor.lastrowid
    except Exception as e:
        print(e)
        conn.rollback()
        return False,None
    

def salvar_dados(path, sinal, observacao):
    status, id_indice = inserir_indice()
    if status:
        status, id_ensaio = inserir_ensaio(st.session_state.nome_ensaio, id_indice, path, sinal, observacao)
        if status:
            atualiza_status_gravacao("Dados salvos com sucesso",True)
        else:
            atualiza_status_gravacao("Erro ao salvar os dados",False)
    else:
        atualiza_status_gravacao("Erro ao salvar os dados",False)


def processa_dados(path):
    sinal = conversor(path,st.session_state.array_dados_indices,st.session_state.tempo_sensor).convert()
    salvar_dados(path, sinal, st.session_state.observacao)
    return path


#TODO: mudar esse cache resource para retirar isso
@st.cache_resource
def conect_obs_socket():
    cl = obs.ReqClient(host='127.0.0.1', port=4455, password='NnjPt4byBxA4DLBC', timeout=3)
    # GetVersion, returns a response object
    resp = cl.get_version()
    # Access it's field as an attribute
    print(f"OBS Version: {resp.obs_version}")
    if resp.obs_version:
        st.session_state.status_conexao_obs = True
        st.session_state.conexao_obs = cl
        return cl
    else:
        st.session_state.status_conexao_obs = False
        st.session_state.conexao_obs = None
        st.error("Falha no OBS")
        return None
    
def start_record(cl):
    cl.set_current_program_scene("Cena")
    cl.start_record()
    st.session_state.recording = True

def stop_record(cl):
    filename = cl.stop_record()
    st.session_state.recording = False
    return filename.output_path

row0 = st.columns(1)
row1 = st.columns(1)
row2 = st.columns(4)
row3 = st.columns(1)
row5 = st.columns(1)


def atualiza_label_status():
    with row3[0]:
        st.write("Status da Gravação:", "Gravando" if st.session_state.recording else "Não Gravando")

def atualiza_status_gravacao(string,flag):
    with row5[0]:
        if flag:
            st.success(string)
        else:
            st.error(string)
            st.session_state.observacao = string



with row0[0]:
    st.title("Ensaio")

with row1[0]:
    st.session_state.nome_ensaio = st.text_input("Nome do Ensaio:")

TIMEOUT = 20
conect_obs_socket()


if st.session_state.connection_status == "Conectado" and st.session_state.conexao_obs:
    with row2[0]:
        if st.button("Iniciar Gravação"):
            if not st.session_state.recording:
                start_record(conect_obs_socket())
                start_time = time.time()
                st.session_state.multiplex_indices_time.append(time.time())
                aux_multiplex = st.session_state.data_multiplex_received_queue[-1]['valor'] +1 if st.session_state.data_multiplex_received_queue[-1]['valor'] != st.session_state.quantidade_sensor else 1
                with st.spinner('Lendo dados...'):
                    time.sleep(((st.session_state.tempo_sensor)/1000))
                    while time.time() - start_time <= (st.session_state.tempo_sensor/1000)* st.session_state.quantidade_sensor + 1:
                        st.session_state.multiplex_indices_time.append(time.time())
                        if time.time() - start_time > TIMEOUT:
                            atualiza_status_gravacao("Erro ao sincronizar gravação com sensores", False)
                            break
                        pass
                    path = stop_record(conect_obs_socket())
                    atualiza_status_gravacao("Gravação finalizada", True)
                with st.spinner("Processando dados..."):
                    array_dados = []
                    ti = st.session_state.multiplex_indices_time[0]
                    tf = st.session_state.multiplex_indices_time[-1]
                    for idx, ob in enumerate(st.session_state.data_multiplex_received_queue):
                        if ti <= ob['tempo'] and ob['tempo'] <= tf:
                            array_dados.append(st.session_state.data_multiplex_received_queue[idx])
                    ob_ind = {
                        "ti": ti,
                        "tf": tf,
                        "array_dados": array_dados
                    }
                    st.session_state.array_dados_indices = ob_ind
                    st.session_state.data_multiplex_received_queue = []
                    time.sleep(2)
                    processa_dados(path)


    with row2[1]:
        if st.button("Parar Gravação"):
            if st.session_state.recording:
                stop_record(conect_obs_socket())
                atualiza_status_gravacao("Gravação interrompida",False)

else:
    if st.session_state.connection_status != "Conectado":
        st.error("Verificar conexão com o equipamento")
    elif not st.session_state.status_conexao_obs:
        st.error("Verificar se o OBS está ativo e configurado corretamente")



