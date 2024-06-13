import os
import time
import platform

tests = (
    'processor_graph_actions.py',
    'get_set_parameters.py',
    'basic_acquire.py',
    'basic_record.py',
    'get_set_recording_info.py',
    'config_audio_device.py',
    'round_trip_record.py',
    'channel_map.py' #TODO: add more plugin specific tests
)

GHA = os.getenv("GITHUB_ACTIONS") == "true"

RECORD_PATH = ''
if platform.system() == 'Windows':
    if GHA: RECORD_PATH = 'C:\\open-ephys\\data'
    else:
        pass #define local path here
elif platform.system() == 'Linux':
    if GHA: pass #RECORD_PATH = '<path/to/linux/runner>'  # TODO
    else:
        pass #define local path here
else: #macos
    if GHA: pass #RECORD_PATH = '<path/to/Mac/runner>'  # TODO
    else: RECORD_PATH = '/Volumes/T7/test-suite/'

for test in tests:
    print("--------------------------------")
    print("Running: ", test[:-3])
    print("--------------------------------")
    rc = os.system(f"python3 ./tests/{test} --parent_directory {RECORD_PATH}")
    if rc != 0:
        print("TEST FAILED: ", test)
        break
    time.sleep(1)