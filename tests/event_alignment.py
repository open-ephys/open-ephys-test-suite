from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import numpy as np

import time

def test(gui, params):

    results = {}

    # Fetch fresh data if needed
    if params['fetch']:

        gui.clear_signal_chain()

        # Build the most simple chain that generates some events
        gui.add_processor("File Reader")
        gui.add_processor("Bandpass Filter")
        gui.add_processor("Phase Detector")
        gui.add_processor("Record Node")

        bpf = gui.get_processors("Bandpass Filter")[0]

        gui.set_parameter(bpf['id'], 0, "low_cut", 1.0)
        gui.set_parameter(bpf['id'], 0, "high_cut", 100.0)

        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], params['engine'])
            gui.set_record_path(node['id'], params['parent_directory'])

        for _ in range(params['num_exp']):

            for _ in range(params['num_rec']):

                gui.acquire()
                time.sleep(params['acq_time'])
                gui.record()
                time.sleep(params['rec_time'])

            gui.idle()

    time.sleep(2)

    # Validate
    session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

    for node in session.recordnodes:

        for rec_idx, recording in enumerate(node.recordings):

            testName = "Event recording"
            if np.abs(len(recording.events) - 168) < 4:
                results[testName] = "PASSED"
            else:
                results[testName] = "FAILED\nExpected: ~ %d\nActual: %d" % (168, len(recording.events))

            #TODO: add more tests

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
    RECORD_PATH = '/Users/pavelkulik/Projects/Allen/OpenEphys/data/test-suite' 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=True, type=int, default=1)
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
