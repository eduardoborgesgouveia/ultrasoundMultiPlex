import queue
import time
import streamlit as st
import serial
import serial.tools.list_ports
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from utils.threadHandler import ThreadHandler
import pickle

st.set_page_config(layout='wide')

if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Desconectado"
if "serial_port" not in st.session_state:
    st.session_state.serial_port = None
if "thread_monitor_serial" not in st.session_state:
    st.session_state.thread_monitor_serial = None
if "acquisition_status" not in st.session_state:
    st.session_state.acquisition_status = "Sem comunicação"
if "thread_update_status" not in st.session_state:
    st.session_state.thread_update_status = None
if "last_acquisition_status" not in st.session_state:
    st.session_state.last_acquisition_status = "Sem comunicação"
if "data_multiplex_received_queue" not in st.session_state:
    st.session_state.data_multiplex_received_queue = []
if "tempo_sensor" not in st.session_state:
    st.session_state.tempo_sensor = 0
if "quantidade_sensor" not in st.session_state:
    st.session_state.quantidade_sensor = 0



# Função para enviar dados pela porta serial
def send_data(serial_port, data):
    serial_port.write(data.encode())

# Função que monitora os valores recebidos pela porta serial
def monitor_serial():
    try:
        received_data = st.session_state.serial_port.readline().decode().strip()
        print("Recebido:", received_data)
        # se a mensagem recebida for "end", finaliza a aquisição
        # se a mensagem recebida for algum número, atualiza o valor da aquisição
        if received_data == "end":
            st.session_state.acquisition_status = "Sem comunicação"
            st.session_state.data_multiplex_received_queue = []
        elif received_data.isdigit():
            # add a pair of timestamp and received data to the data_multiplex_received_queue
            st.session_state.data_multiplex_received_queue.append({'tempo':time.time(), 'valor':int(received_data)})
            if len(st.session_state.data_multiplex_received_queue) > 500:
                st.session_state.data_multiplex_received_queue = st.session_state.data_multiplex_received_queue[1:]
            st.session_state.acquisition_status = "Em andamento"
        if st.session_state.last_acquisition_status != st.session_state.acquisition_status:
            st.session_state.last_acquisition_status = st.session_state.acquisition_status
            update_status()

    except:
        print("Erro ao receber dados")



# Configurações da interface
st.title("Conexão Equipamento")


row1 = st.columns(2)
row2 = st.columns(4)
row3 = st.columns(2)
row4 = st.columns(1)
row5 = st.columns(1)
row6 = st.columns(1)

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    serial_ports = []
    for port, desc, hwid in sorted(ports):
        serial_ports.append(port)
    return serial_ports

def update_status():
    time.sleep(2)
    with row4[0]:
        st.write("Status da Conexão:", st.session_state.connection_status)
    with row5[0]:
        st.write("Status da Comunicação:", st.session_state.acquisition_status)

def connect_serial():
    try:
        # Tentar conectar à porta serial
        serial_port = serial.Serial(selected_interface, selected_baudrate, timeout=1)
        st.session_state.connection_status = "Conectado"
        st.session_state.serial_port = serial_port
        return serial_port
    except serial.SerialException:
        st.error("Falha ao conectar. Verifique a porta serial selecionada.")
        return None

# Lista das interfaces possíveis (COM ports no Windows, /dev/tty* no Linux/Mac)
serial_interfaces = list_serial_ports()
with row1[0]:
    selected_interface = st.selectbox("Selecione a interface serial:", serial_interfaces)
    st.markdown("#")

# Baudrates possíveis
baudrates = [115200]  # Adicione as baudrates necessárias
with row1[1]:
    selected_baudrate = st.selectbox("Selecione a baudrate:", baudrates)
    st.markdown("#")

with row2[0]:
    # Botão de conectar
    if st.button("Conectar"):
        try:
            if st.session_state.connection_status == "Conectado":
                st.error("Já conectado. Desconecte antes de tentar conectar novamente.")
            else:
                # Tentar conectar à porta serial
                print(selected_interface, selected_baudrate)
                serial_port = connect_serial()

                # Iniciar a thread de monitoramento serial
                monitor_thread = ThreadHandler(monitor_serial)
                ctx = get_script_run_ctx()
                add_script_run_ctx(thread=monitor_thread.thread, ctx=ctx)
                st.session_state.thread_monitor_serial = monitor_thread
                monitor_thread.start()
                # update_status()
        except serial.SerialException:
            st.error("Falha ao conectar. Verifique a porta serial selecionada.")
    st.markdown("#")

with row2[1]:
    if st.button("Desconectar"):
        try:
            if st.session_state.connection_status == "Conectado":
                st.session_state.serial_port.close()
                st.session_state.connection_status = "Desconectado"
                st.session_state.acquisition_status = "Finalizado"
                st.session_state.thread_monitor_serial.pause()
                st.session_state.thread_monitor_serial.kill()
                # update_status()
            else:
                st.error("Já desconectado. Conecte antes de tentar desconectar novamente.")
        except:
            st.error("Falha ao desconectar. Verifique a porta serial selecionada.")
    st.markdown("#")



# Campo para enviar dados pela porta serial
if st.session_state.connection_status == "Conectado":
    with row3[0]:
        data_to_send = st.text_input("Enviar dados pela porta serial:")
        st.markdown("#")
    with row3[1]:
        st.markdown("#")
        if st.button("Enviar"):
            tempo = data_to_send.split(",")[0]
            quantidade = data_to_send.split(",")[1]
            if tempo.isdigit() and quantidade.isdigit():
                st.session_state.tempo_sensor = int(tempo)
                st.session_state.quantidade_sensor = int(quantidade)
                send_data(st.session_state.serial_port, data_to_send)
                # update_status()
            else:
                st.error("Digite um valor numérico válido. Formato <<tempo,quantidade>>")


update_status()

