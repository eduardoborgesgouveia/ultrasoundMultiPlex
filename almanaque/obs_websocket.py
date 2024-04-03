import obsws_python as obs

# pass conn info if not in config.toml
cl = obs.ReqClient(host='127.0.0.1', port=4455, password='fKS5qRhjO5O1qtUk', timeout=3)

# # load conn info from config.toml
# cl = obs.ReqClient()

# GetVersion, returns a response object
resp = cl.get_version()
# Access it's field as an attribute
print(f"OBS Version: {resp.obs_version}")


# SetCurrentProgramScene
cl.set_current_program_scene("Cena")



# start recording
cl.start_record()

# wait 10 seconds
import time
time.sleep(3)

# stop recording
filename = cl.stop_record()
print(f"Recording saved as {filename.output_path}")



