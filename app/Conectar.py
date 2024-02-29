import streamlit as st
import serial
import threading
import serial.tools.list_ports


# Função para enviar dados pela porta serial
def send_data(serial_port, data):
    serial_port.write(data.encode())


# Função que monitora os valores recebidos pela porta serial
def monitor_serial(serial_port):
    while True:
        received_data = serial_port.readline().decode().strip()
        st.write("Recebido:", received_data)
        if received_data == "end":
            st.session_state.connection_status = "Finalizado"
            break


# Configurações da interface
st.title("Conexão Serial")


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    serial_ports = []
    for port, desc, hwid in sorted(ports):
        serial_ports.append(port)
    return serial_ports


# Lista das interfaces possíveis (COM ports no Windows, /dev/tty* no Linux/Mac)
serial_interfaces = list_serial_ports()
selected_interface = st.selectbox("Selecione a interface serial:", serial_interfaces)

# Baudrates possíveis
baudrates = [9600, 19200, 38400, 57600, 115200]  # Adicione as baudrates necessárias
selected_baudrate = st.selectbox("Selecione a baudrate:", baudrates)

# Botão de conectar
if st.button("Conectar"):
    try:
        # Tentar conectar à porta serial
        print(selected_interface, selected_baudrate)
        serial_port = serial.Serial(selected_interface, selected_baudrate, timeout=1)
        st.session_state.connection_status = "Conectado"

        # Iniciar a thread de monitoramento serial
        monitor_thread = threading.Thread(target=monitor_serial, args=(serial_port,))
        monitor_thread.start()
    except serial.SerialException:
        st.error("Falha ao conectar. Verifique a porta serial selecionada.")

# Mostrar status da conexão
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Desconectado"
st.write("Status da Conexão:", st.session_state.connection_status)

# Campo para enviar dados pela porta serial
if st.session_state.connection_status == "Conectado":
    data_to_send = st.text_input("Enviar dados pela porta serial:")
    if st.button("Enviar"):
        send_data(serial_port, data_to_send)
