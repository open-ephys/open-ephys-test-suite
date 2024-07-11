from open_ephys.control import OpenEphysHTTPServer

import os.path

"""
Test Name: Processor Graph Actions
Test Description: Validates actions performed to build/modify the Processor Graph
"""

def test(gui, params):

    results = {}

    with open(params['cfg_path'], 'r', encoding='utf-8') as file:
        gt_config = file.read()

    testName = 'Clear signal chain'

    gui.clear_signal_chain()

    condition = len(gui.get_processors()) == 0
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count: " + str(len(gui.get_processors()))

    testName = 'Load signal chain'

    gui.load(params['cfg_path'])

    loaded_config = gui.get_config()

    condition = len(gui.get_processors()) > 0
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count: " + str(len(gui.get_processors()))

    #TODO: compare to gt_config to validate load, ignoring local tags
    #print(gui.get_config()['info'] == gt_config)

    testName = 'Save configuration'

    full_path = '/Volumes/T7/test-suite/testConfig3.xml'
    gui.save(full_path)

    condition = os.path.exists(full_path)
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tFile not saved"

    testName = 'Add processor to an existing chain'

    numProcessorsBeforeAdd = len(gui.get_processors())
    gui.add_processor("Bandpass Filter")

    numProcessorsAfterAdd = len(gui.get_processors())

    condition = numProcessorsAfterAdd == numProcessorsBeforeAdd + 1
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)

    testName = 'Delete processor'

    mostRecentlyAddedProcessorId = max(gui.get_processors(), key=lambda processor: processor['id'])['id']
    gui.delete_processor(mostRecentlyAddedProcessorId)

    numProcessorsBeforeDelete = numProcessorsAfterAdd
    numProcessorsAfterDelete = len(gui.get_processors())

    condition = numProcessorsAfterDelete == numProcessorsBeforeDelete - 1
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count before delete: " + str(numProcessorsBeforeDelete) + " after: " + str(numProcessorsAfterDelete)

    testName = 'Add processor to empty signal chain'

    numProcessorsBeforeAdd = numProcessorsAfterDelete
    gui.add_processor("File Reader")
    numProcessorsAfterAdd = len(gui.get_processors())
    condition = numProcessorsAfterAdd == numProcessorsBeforeAdd + 1
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count before add: " + str(numProcessorsBeforeAdd) + " after: " + str(numProcessorsAfterAdd)

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