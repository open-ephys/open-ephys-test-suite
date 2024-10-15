import time
import os.path

from open_ephys.control import OpenEphysHTTPServer

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

    time.sleep(1)

    condition = len(gui.get_processors()) == 0
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count: " + str(len(gui.get_processors()))

    testName = 'Load signal chain'

    gui.load(params['cfg_path'])

    time.sleep(1)

    loaded_config = gui.get_config()

    condition = len(gui.get_processors()) > 0
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tProcessor count: " + str(len(gui.get_processors()))

    #TODO: compare to gt_config to validate load, ignoring local tags
    #print(gui.get_config()['info'] == gt_config)

    testName = 'Save configuration'

    full_path = os.path.join(params['parent_directory'], 'test_config.xml')
    gui.save(full_path)

    condition = os.path.exists(full_path)
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tFile not saved"

    #delete saved file
    if os.path.exists(full_path):
        os.remove(full_path)

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

    parser = argparse.ArgumentParser(description='Test Processor Graph Actions')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=5)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=1)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)