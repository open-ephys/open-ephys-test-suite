from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import time 

def test(gui, params):

    # Fetch fresh data if needed
    if params['fetch']: 

        results = {}

        gui.load(params['cfg_path'])

        gui.set_prepend_text(params['prepend_text'])
        gui.set_base_text(params['base_text'])
        gui.set_append_text(params['append_text'])
        gui.set_parent_dir(params['parent_directory'])

        # Set all record node engines
        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], params['engine'])

        # Add record node after Spike Viewer
        gui.add_processor("Record Node")

        nodeDirectories = {}
        for node in gui.get_recording_info()['record_nodes']:
            nodeDirectories[node['node_id']] = node['parent_directory']
            print("%d : %s" % (node['node_id'], node['parent_directory']))

        # Only latest RecordNode will have the newly set parent directory
        testName = 'Set Recording Locations'

        for node in gui.get_recording_info()['record_nodes']:
            print(node['parent_directory'])

        # Run some actions and record data
        for n in range(params['num_exp']):

            #Start a new directory only for the third experiment
            if n == 2:
                gui.set_start_new_dir()

            for _ in range(params['num_rec']):

                gui.acquire()
                time.sleep(params['acq_time'])
                gui.record(params['rec_time'])

            gui.idle()

    #Find the expected recordings
    for node, dir in nodeDirectories.items():
        if len(gui.get_latest_recordings(dir, count=2)) == 2:
            results[testName] = "PASSED"
        else:
            results[testName] = "FAILED\n\tExpected 2 recordings in %s, found %d" % (dir, len(gui.get_latest_recordings(dir, count=2)))

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
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, 'file_reader_config.xml'))
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