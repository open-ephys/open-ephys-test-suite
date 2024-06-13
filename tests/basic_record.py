import time

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

"""
Test Name: Minimal Recording
Test Description: Record and check data from the default signal chain
"""

SET_RECORD_PATH = True

def test(gui, params):

    results = {}

    # Fetch fresh data if needed
    if params['fetch']:

        # Load config for this test
        gui.load(params['cfg_path'])

        if SET_RECORD_PATH:
            for node in gui.get_processors("Record Node"):
                gui.set_record_engine(node['id'], params['engine'])
                gui.set_record_path(node['id'], params['parent_directory'])

        # Run some actions and record data
        for _ in range(params['num_exp']):

            for _ in range(params['num_rec']):

                gui.acquire()
                time.sleep(params['acq_time'])
                gui.record()
                time.sleep(params['rec_time'])

            gui.idle()

    # Validate results
    show = False
    session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

    if show: print(session)

    for node_idx, node in enumerate(session.recordnodes):

        testName = "Total recordings"
        if len(node.recordings) == params['num_rec']*params['num_exp']:
            results[testName] = "PASSED"
        else:
            results[testName] = "FAILED\nExpected: %d\nActual: %d" % (params['num_rec']*params['num_exp'], len(node.recordings))

        for rec_idx, recording in enumerate(node.recordings):

            for str_idx, stream in enumerate(recording.continuous):

                SAMPLE_RATE = stream.metadata['sample_rate']

                SAMPLE_NUM_TOLERANCE = 0.1 * SAMPLE_RATE

                testName = "Recording %d length" % (rec_idx+1)
                if np.absolute(len(stream.timestamps) - params['rec_time']*SAMPLE_RATE) < SAMPLE_NUM_TOLERANCE:
                    results[testName] = "PASSED"
                else:
                    results[testName] = "FAILED\nExpected: %d\nActual: %d" % (len(stream.timestamps), params['rec_time']*stream.metadata['sample_rate'])

                #print first few samples, sample_numbers and timestamps in 3 cols
                if show:
                    print("Sample Number\tTimestamp\tData")
                    for i in range(10):
                        print("%d\t\t%.5f\t\t%.3f" % (stream.sample_numbers[i], stream.timestamps[i], stream.samples[i,1]))

    return results


'''
================================================================================================================================================
'''
import os
import sys
import argparse
import platform

from pathlib import Path

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default='C:\\open-ephys\\data')
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
