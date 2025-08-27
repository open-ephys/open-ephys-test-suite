from open_ephys.control import OpenEphysHTTPServer

def test(gui, params):

    results = {}

    # Load config for this test
    gui.load(params['cfg_path'])

    # Get the first bandpass filter
    bandpass_filter = gui.get_processors("Bandpass Filter")[0]

    # Set the low pass cutoff frequency in Hz
    testName = "Set low pass cutoff frequency"
    testValue = 350.0
    gui.set_stream_parameter(bandpass_filter['id'], 0, 'low_cut', testValue)

    bandpass_filter = gui.get_processors("Bandpass Filter")[0]

    for param in bandpass_filter["streams"][0]["parameters"]:
        if param["name"] == 'low_cut':
            condition = float(param["value"]) == testValue
            if condition: results[testName] = "PASSED"
            else: results[testName] = "FAILED\n\tLow pass cutoff frequency expected: %s actual: %s" % (testValue, param["value"])

    record_node = gui.get_processors("Record Node")[0]

    #print(record_node["streams"][0]["parameters"])

    for param in record_node["streams"][0]["parameters"]:
        if param["name"] == 'record_path':
            condition = param["value"] == RECORD_PATH
            if condition: results["Set record path"] = "PASSED"
            else: results["Set record path"] = "FAILED\n\tRecord path expected: %s actual: %s" % (RECORD_PATH, param["value"])

    gui.clear_signal_chain()

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
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../../configs/file_reader_config.xml'))
    parser.add_argument('--parent_directory', required=False, type=str, default='C:\\open-ephys\\data')
    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)