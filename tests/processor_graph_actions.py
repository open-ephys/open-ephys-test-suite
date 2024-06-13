from open_ephys.control import OpenEphysHTTPServer

import os.path

"""
Test Name: Processor Graph Actions
Test Description: Validates actions performed to build/modify the Processor Graph
"""

def test(gui, params):

    results = {}

    gui.load(params['cfg_path'])

    numProcessorsBeforeAdd = len(gui.get_processors())

    testName = 'Add processor to an existing chain'
    gui.add_processor("Bandpass Filter")

    numProcessorsAfterAdd = len(gui.get_processors())

    if numProcessorsAfterAdd == numProcessorsBeforeAdd + 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)

    testName = 'Delete processor'
    mostRecentlyAddedProcessorId = max(gui.get_processors(), key=lambda processor: processor['id'])['id']
    gui.delete_processor(mostRecentlyAddedProcessorId)

    numProcessorsBeforeDelete = numProcessorsAfterAdd
    numProcessorsAfterDelete = len(gui.get_processors())

    if numProcessorsAfterDelete == numProcessorsBeforeDelete - 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before delete: " + str(numProcessorsBeforeDelete) + " after: " + str(numProcessorsAfterDelete)

    testName = 'Clear the signal chain'
    gui.clear_signal_chain()

    numProcessorsBeforeClear = numProcessorsAfterDelete
    numProcessorsAfterClear = len(gui.get_processors())
    if numProcessorsAfterClear == 0:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before clear: " + str(numProcessorsBeforeClear) + " after: " + str(numProcessorsAfterClear)

    testName = 'Add processor to empty signal chain'

    numProcessorsBeforeAdd = numProcessorsAfterClear
    gui.add_processor("File Reader")
    numProcessorsAfterAdd = len(gui.get_processors())
    if numProcessorsAfterAdd == numProcessorsBeforeAdd + 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)

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
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--parent_directory', required=False, type=str, default='C:\\open-ephys\\data')
    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)