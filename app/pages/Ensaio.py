import time
import streamlit as st
import numpy as np
import obsws_python as obs

if "recording" not in st.session_state:
    st.session_state.recording = False

if "nome_ensaio" not in st.session_state:
    st.session_state.nome_ensaio = ""

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
if st.button("Iniciar Gravação"):
    start_record(conect_obs_socket())
    idx_inicial = st.session_state.data_multiplex_received_queue[-1]
    with st.spinner('Lendo dados...'):
        time.sleep(0.5)
        start_time = time.time()
        while st.session_state.data_multiplex_received_queue[-1] != idx_inicial:
            if time.time() - start_time > TIMEOUT:
                st.error("Erro ao iniciar gravação")
                break
            pass
        stop_record(conect_obs_socket())




if st.button("Parar Gravação"):
    stop_record(conect_obs_socket())
st.write("Status da Gravação:", "Gravando" if st.session_state.recording else "Não Gravando")
    
