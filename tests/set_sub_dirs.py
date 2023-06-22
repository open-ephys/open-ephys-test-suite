from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import time 

def test(gui, params):

    results = {}

    # Load config for this test
    if params['mode'] == 'local':
        gui.load(params['cfg_path'])

    # Set the first Record Node to a non existent directory
    for node in gui.get_recording_info()['record_nodes']:
        gui.set_record_path(node['node_id'], params['parent_directory'])
        break

    # Validate the recording directories 
    nodeDirectories = {}
    for node in gui.get_recording_info()['record_nodes']:
        nodeDirectories[node['node_id']] = node['parent_directory']

    testName = 'Set New SubDir For Recording'

    # Acquire and record data
    for n in range(params['num_exp']):

        for _ in range(params['num_rec']):

            gui.acquire()
            time.sleep(params['acq_time'])
            gui.record()
            time.sleep(params['rec_time'])

        gui.idle()

    time.sleep(2)
    gui.quit()

    #Find the expected recording from the first RecordNode
    for node, dir in nodeDirectories.items():
        if len(gui.get_latest_recordings(dir, count=1)) == 1:
            results[testName+" | "+dir] = "PASSED"
        else:
            results[testName+" | "+dir] = "FAILED\n\tExpected 1 recording in %s, found %d" % (dir, len(gui.get_latest_recordings(dir, count=2)))

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
    RECORD_PATH = 'D:\\test-suite\\data\\new-sub-dir1\\new-sub-dir2'
elif platform.system() == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    RECORD_PATH = '/Users/pavelkulik/Documents/Open Ephys/new-sub-dir1/new-sub-dir2'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=True, type=int, default=1)
    parser.add_argument('--address', required=False, type=str, default='http://127.0.0.1')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=5)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=3)
    parser.add_argument('--prepend_text', required=False, type=str, default='alice')
    parser.add_argument('--base_text', required=False, type=str, default='test')
    parser.add_argument('--append_text', required=False, type=str, default='auto')
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)