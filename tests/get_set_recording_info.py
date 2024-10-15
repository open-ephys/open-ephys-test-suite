from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import os
import time

"""
Test Name: Set recording info
Test Description: Set recording names and locations for Record Nodes
"""
def test(gui, params):

    # Fetch fresh data if needed
    if params['fetch']: 

        results = {}

        gui.load(params['cfg_path'])

        gui.set_prepend_text(params['prepend_text'])
        gui.set_base_text(params['base_text'])
        gui.set_append_text(params['append_text'])

        time.sleep(3)
        
        # Set a new parent directory to get applied to new RecordNodes
        os.makedirs(os.path.join(params['parent_directory'], 'test'), exist_ok=True)
        gui.set_parent_dir(os.path.join(params['parent_directory'], 'test'))

        # Set all record node paths and engines
        for node in gui.get_processors("Record Node"):
            gui.set_record_path(node['id'], params['parent_directory'])
            gui.set_record_engine(node['id'], params['engine'])

        # Add record node after Spike Viewer
        gui.add_processor("Record Node") # (should use new parent dir)

        # Check only the latest RecordNode has the new parent directory
        nodeDirectories = {}
        for node in gui.get_recording_info()['record_nodes']:
            nodeDirectories[node['node_id']] = node['parent_directory']
            print(f"Set path for Record Node {node['node_id']} to {node['parent_directory']}")

        testName = 'Set recording names and locations'

        # Run some actions and record data
        for n in range(params['num_exp']):

            #Start a new directory only for the third experiment
            if n == 2: gui.set_start_new_dir()

            for _ in range(params['num_rec']):

                gui.acquire()
                time.sleep(params['acq_time'])
                gui.record()
                time.sleep(params['rec_time'])

            gui.idle()

    root_folder = params['prepend_text'] + params['base_text'] + params['append_text']

    #Find the expected recordings
    for node, dir in nodeDirectories.items():
        condition = len(gui.get_latest_recordings(os.path.join(dir, root_folder))) == 1
        if condition: results[f"Recording write path for Record Node {node}"] = "PASSED"
        else: results[f"Recording write path for Record Node {node}"] = "FAILED"

    # reset to default settings
    gui.set_prepend_text('')
    gui.set_base_text('auto')
    gui.set_append_text('')

    #TODO: Make sure resetting to default works

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
    parser.add_argument('--prepend_text', required=False, type=str, default='abc')
    parser.add_argument('--base_text', required=False, type=str, default='main')
    parser.add_argument('--append_text', required=False, type=str, default='xyz')
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)