import os
import time
import platform
from datetime import datetime

gui_tests = (
    'processor_graph_actions.py',
    'get_set_parameters.py',
    'basic_acquire.py',
    'basic_record.py',
    'get_set_recording_info.py',
    'config_audio_device.py',
    'round_trip_record.py',
)

#TODO: Add more plugin tests
plugin_tests = (
    'channel_map.py',
)

if platform.system() == 'Windows':
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_WINDOWS_GITHUB_RECORD_PATH')
    else:  # custom local path
        RECORD_PATH = os.getenv('OE_WINDOWS_LOCAL_RECORD_PATH')
elif platform.system() == 'Linux':
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_LINUX_GITHUB_RECORD_PATH')
    else:  # custom local path
        RECORD_PATH = os.getenv('OE_LINUX_LOCAL_RECORD_PATH')
else:
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_MAC_GITHUB_RECORD_PATH')
    else:  # custom local path
        RECORD_PATH = os.getenv('OE_MAC_LOCAL_RECORD_PATH')

for test in gui_tests + plugin_tests:
    print("--------------------------------")
    print("Running: ", test[:-3])
    print("Start time: ", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), flush=True)
    print("--------------------------------")
    rc = os.system(f"python3 ./tests/{test}")
    if rc != 0:
        print("TEST FAILED: ", test)
        break

    #remove any files that were created during the current test
    os.system("rm -rf " + RECORD_PATH + "/*")

    time.sleep(1)
