import random
import streamlit as st
import threading
import time

# Use a session state variable to track connection status
if "connected" not in st.session_state:
    st.session_state["connected"] = False


def is_connected():
    return random.choice([True, False])

def check_connection():
    while True:
        # Simulate a connection check (replace with your actual logic)
        time.sleep(2)
        if is_connected():  # Replace with your actual connection check
            st.session_state["connected"] = True
        else:
            st.session_state["connected"] = False

        # Safely trigger a Streamlit rerun from the thread
        st.experimental_rerun()

# Create the thread and start it
thread = threading.Thread(target=check_connection)
thread.start()

# Display the connection status on the screen
st.title("Connection Status")
connection_status = st.empty()

while True:
    if st.session_state["connected"]:
        connection_status.text("Connected")
    else:
        connection_status.text("Disconnected")

    time.sleep(1)


