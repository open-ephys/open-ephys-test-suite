from open_ephys.control import OpenEphysHTTPServer

import time

"""
Test Name: Add/Delete Processor
Test Description: Add and delete a processor from the signal chain
"""

def test(gui, params):

    # Store test results to report in a dictionary
    results = {}

    # Load config for this test
    if params['mode'] == 'local':
        gui.load(params['cfg_path'])

    # Get list of processors in signal chain
    numProcessorsBeforeAdd = len(gui.get_processors())

    # Add a processor to end of signal chain
    testName = 'Add processor to existing chain'
    gui.add_processor("Bandpass Filter")

    numProcessorsAfterAdd = len(gui.get_processors())

    if numProcessorsAfterAdd == numProcessorsBeforeAdd + 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)

    # Delete the most recently added processor
    testName = 'Delete processor'
    mostRecentlyAddedProcessorId = max(gui.get_processors(), key=lambda processor: processor['id'])['id']
    gui.delete_processor(mostRecentlyAddedProcessorId)

    numProcessorsBeforeDelete = numProcessorsAfterAdd
    numProcessorsAfterDelete = len(gui.get_processors())

    if numProcessorsAfterDelete == numProcessorsBeforeDelete - 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before delete: " + str(numProcessorsBeforeDelete) + " after: " + str(numProcessorsAfterDelete)

    # Clear signal chain
    testName = 'Clear the signal chain'
    gui.clear_signal_chain()

    numProcessorsBeforeClear = numProcessorsAfterDelete
    numProcessorsAfterClear = len(gui.get_processors())
    if numProcessorsAfterClear == 0:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before clear: " + str(numProcessorsBeforeClear) + " after: " + str(numProcessorsAfterClear)

    # Add processor to empty signal chain
    testName = 'Add processor to empty signal chain'

    numProcessorsBeforeAdd = numProcessorsAfterClear
    gui.add_processor("File Reader")
    numProcessorsAfterAdd = len(gui.get_processors())

    if numProcessorsAfterAdd == numProcessorsBeforeAdd + 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)


    gui.quit()

    time.sleep(2)

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