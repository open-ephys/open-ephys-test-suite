from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import time 

def test(gui, params):

    results = {}

    print("Running test...")

    # Generate an activity log that contains logging from a plugin
    if params['fetch']:

        # Add a plugin processor
        gui.add_processor('Bandpass Filter')

        time.sleep(2)

        gui.quit()

        time.sleep(2)

    testName = 'Validate plugins log message to log file'

    # Find the most recent log file
    log_path = params['log_path']
    log_files = [f for f in os.listdir(log_path) if 'activity' in f]
    log_files.sort()
    most_recent = log_files[-1]

    # Read the log file
    with open(os.path.join(log_path, most_recent), 'r') as f:
        log = f.read()
        #Only print lines that contain the plugin name
        log = [line for line in log.split('\n') if '[FilterNode]' in line]
        if (len(log) > 0):
            results[testName+' | '+most_recent] = "PASSED"
        else:
            results[testName] = "FAILED\n\tNo log messages from plugin found in log file"

    return results

'''
================================================================================================================================================
'''
import os
import sys
import argparse
import platform

from pathlib import Path

if platform.system() == 'Windows':
    RECORD_PATH = 'C:\\open-ephys\\data'
elif platform.system() == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    LOG_PATH = '/Users/pavelkulik/Library/Application Support/open-ephys/configs-api9/'
    RECORD_PATH = '<path/to/mac/runner>' #TODO

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--address', required=False, type=str, default='http://127.0.0.1')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--log_path', required=False, type=str, default=LOG_PATH)
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=2)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=3)
    parser.add_argument('--prepend_text', required=False, type=str, default='auto')
    parser.add_argument('--base_text', required=False, type=str, default='auto')
    parser.add_argument('--append_text', required=False, type=str, default='auto')
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)