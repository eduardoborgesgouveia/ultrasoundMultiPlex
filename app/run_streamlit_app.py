import subprocess
import logging
import time


def run_streamlit_app(file_path, log_file="streamlit.log"):
    """
    Run a Streamlit application via terminal.

    Parameters:
        file_path (str): Path to the Python script containing the Streamlit application.
        port (int): Port number to run the Streamlit application (default is 8501).
    """
    command = f"C:/Users/lmest_udvn8rw/Documents/projetos/ultrasoundMultiPlex/.venv/Scripts/activate.bat && streamlit run {file_path} --server.port 80 "
    with open(log_file, "w") as log:
        subprocess.run(command, shell=True, stdout=log, stderr=subprocess.STDOUT)

    input("Ctrl+C to stop the Streamlit app.")


if __name__ == "__main__":
    logging.basicConfig(filename='streamlit_app.log', level=logging.INFO)
    # Replace 'app.py' with the path to your Streamlit application file
    run_streamlit_app("C:/Users/lmest_udvn8rw/Documents/projetos/ultrasoundMultiPlex/app/Conectar_Equipamento.py","streamlit_app.log")