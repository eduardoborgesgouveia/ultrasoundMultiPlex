from datetime import datetime
import pickle
import sqlite3
import time
import streamlit as st
import numpy as np
import obsws_python as obs
from utils.convert_video_data import conersor

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


## TODO: colocar banco de dados como uma classe
## conexão db para salvar os dados
## banco sqlite armazenado em db/db.sqlite
def conect_db():
    # conecta com o banco de dados
    conn = sqlite3.connect("./app/db/db")
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
            st.success("Dados salvos com sucesso")
        else:
            st.error("Erro ao salvar os dados")
    else:
        st.error("Erro ao salvar os dados")


def processa_dados(path):
    sinal = conersor(path,st.session_state.array_dados_indices,st.session_state.tempo_sensor).convert()
    salvar_dados(path, sinal, "observacao")
    return path



@st.cache_resource
def conect_obs_socket():
    cl = obs.ReqClient(host='127.0.0.1', port=4455, password='fKS5qRhjO5O1qtUk', timeout=3)
    # GetVersion, returns a response object
    resp = cl.get_version()
    # Access it's field as an attribute
    print(f"OBS Version: {resp.obs_version}")
    if resp.obs_version:
        return cl
    else:
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

st.title("Ensaio")

# colocar um campo de texto para o usuário colocar o nome do ensaio
# colocar um botão para iniciar a gravação
# colocar um botão para parar a gravação
# mostrar o status da gravação

st.session_state.nome_ensaio = st.text_input("Nome do Ensaio:")
TIMEOUT = 30
# TODO: verificar se a conexão com o equipamento está ativa e coletando 
# TODO: verificar se a conexão com o OBS está ativa
# TODO: criar uma variavel de observação para armazenar se todo o processo foi ok ou se saiu pelo timeout etc.
if st.button("Iniciar Gravação"):
    start_record(conect_obs_socket())
    start_time = time.time()
    st.session_state.multiplex_indices_time.append(time.time())
    aux_multiplex = st.session_state.data_multiplex_received_queue[-1]['valor'] +1 if st.session_state.data_multiplex_received_queue[-1]['valor'] != st.session_state.quantidade_sensor else 1
    with st.spinner('Lendo dados...'):
        # TODO: separar o vídeo por canais e salvar os dados separados
        # talvez gerar um objeto gigante com vários sinais pra não mexer no banco
        time.sleep((st.session_state.tempo_sensor)/1000)
        while time.time() - start_time <= (st.session_state.tempo_sensor/1000)* st.session_state.quantidade_sensor + 1:
            st.session_state.multiplex_indices_time.append(time.time())
            if time.time() - start_time > TIMEOUT:
                st.error("Erro ao sincronizar gravação com sensores")
                break
            pass
        path = stop_record(conect_obs_socket())
        st.success("Gravação finalizada")
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
            processa_dados(path)



if st.button("Parar Gravação"):
    stop_record(conect_obs_socket())
    st.error("Gravação interrompida")
st.write("Status da Gravação:", "Gravando" if st.session_state.recording else "Não Gravando")

    


