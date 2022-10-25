from open_ephys.control import OpenEphysHTTPServer

import time

def test(gui, params):

    results = {}

    # Load config for this test
    if params['mode'] == 'local':
        gui.load(params['cfg_path'])

    # Get the first bandpass filter
    bandpass_filter = gui.get_processors("Bandpass Filter")[0]

    # Set the low pass cutoff frequency in Hz
    testName = "Set low pass cutoff frequency"
    testValue = 350.0
    gui.set_param(bandpass_filter['id'], 0, 'low_cut', testValue)

    bandpass_filter = gui.get_processors("Bandpass Filter")[0]

    for param in bandpass_filter["streams"][0]["parameters"]:
        if param["name"] == 'low_cut':
            if float(param["value"]) == testValue:
                results[testName] = "PASSED"
            else:
                results[testName] = "FAILED\n\tLow cut value expected: %d actual: %d" % (str(testValue), param["value"])
            
    gui.quit()

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
    RECORD_PATH = '<path/to/mac/runner>' #TODO

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=False, default=True, action='store_true')
    parser.add_argument('--address', required=False, type=str, default='http://127.0.0.1')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=5)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=1)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)