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
            condition = float(str(param["value"]).split(' ')[0]) == testValue
            if condition: results[testName] = "PASSED"
            else: results[testName] = "FAILED\n\tLow pass cutoff frequency expected: %s actual: %s" % (testValue, param["value"])

    record_node = gui.get_processors("Record Node")[0]

    #print(record_node["streams"][0]["parameters"])

    for param in record_node["streams"][0]["parameters"]:
        if param["name"] == 'record_path':
            condition = param["value"] == params['parent_directory']
            if condition: results["Set record path"] = "PASSED"
            else: results["Set record path"] = "FAILED\n\tRecord path expected: %s actual: %s" % (params['parent_directory'], param["value"])

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../../configs/file_reader_config.xml'))
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)