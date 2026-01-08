import os
import sys
import time
import platform
from datetime import datetime
import subprocess

def log(msg): print(f'[test-suite] {msg}', flush=True)

gui_tests = (
    os.path.join('core', 'processor_graph_actions.py'),
    os.path.join('core', 'get_set_parameters.py'),
    os.path.join('core', 'basic_acquire.py'),
    os.path.join('core', 'basic_record.py'),
    os.path.join('core', 'get_set_recording_info.py'),
    #'config_audio_device.py',
    os.path.join('core', 'round_trip_record.py'),
)

#TODO: Add more built-inplugin tests
plugin_tests = (
    os.path.join('plugins', 'channel_map.py'),
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

if not RECORD_PATH:
    raise RuntimeError(
        "RECORD_PATH is not set. Define one of the OE_*_RECORD_PATH environment variables "
        "for your OS (e.g. OE_WINDOWS_LOCAL_RECORD_PATH)."
    )

log("Starting test suite")
log("Clearing existing recordings")
os.system("rm -rf " + RECORD_PATH + "/*")

for test in gui_tests + plugin_tests:
    log(f"Running: {test[:-3]}")
    log(f"Start time: {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    
    test_path = os.path.join('tests', test)
    log(f"Executing: {sys.executable} {test_path}")

    completed = subprocess.run([sys.executable, test_path])

    if completed.returncode != 0:
        log(f"TEST FAILED: {test} (exit code: {completed.returncode})")
        log(f"Check output above for error details")
        sys.exit(completed.returncode)
    
    log(f"Test completed successfully: {test}")
    log(f"End time: {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")

    #remove any files that were created during the current test
    CLEAR_RECORDINGS = False
    if CLEAR_RECORDINGS:
        log("Clearing existing recordings")
        os.system("rm -rf " + RECORD_PATH + "/*")

log("All tests completed successfully")