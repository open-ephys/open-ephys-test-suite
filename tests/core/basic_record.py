import time

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

"""
Test Name: Minimal Recording
Test Description: Record and check data from the default signal chain
"""

def test(gui, params):

    results = {}

    # Fetch fresh data if needed
    if params['fetch']:

        # Load config for this test
        gui.load(params['cfg_path'])

        # Apply custom data recording parameters
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
    dir_ = params['parent_directory']
    print(dir_)
    session = Session(gui.get_latest_recordings(dir_)[0])

    for node_idx, node in enumerate(session.recordnodes):

        # Validate total number of recordings
        testName = "Total recordings"
        condition = len(node.recordings) == params['num_rec']*params['num_exp']
        if condition: results[testName] = "PASSED"
        else: results[testName] = "FAILED\nExpected: %d\nActual: %d" % (params['num_rec']*params['num_exp'], len(node.recordings))

        for rec_idx, recording in enumerate(node.recordings):

            for _, stream in enumerate(recording.continuous):

                # Validate amount of continuous data recorded is within range
                testName = f"Recording {rec_idx+1} data size"
                expected_samples = params['rec_time'] * stream.metadata['sample_rate']
                condition = np.isclose(len(stream.timestamps), expected_samples, atol=0.05 * expected_samples)
                if condition: results[testName] = "PASSED"
                else: results[testName] = "FAILED\nExpected: %d\nActual: %d" % (expected_samples, len(stream.timestamps))

                # Validate spikes were written in the second record node
                testName = f"Recording {rec_idx+1} spike count"
                condition = node_idx  == 1 and len(recording.spikes) > 0
                if condition: results[testName] = "PASSED"
                else: results[testName] = "FAILED\nExpected: >0\nActual: %d" % len(recording.spikes)

                # TODO: Save spike data to be used to verify channel mapper downstream.
                # for spike_channel in recording.spikes:
                #     print(f"{spike_channel.metadata['name']} : {len(spike_channel.sample_numbers)} spikes")

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

    parser = argparse.ArgumentParser(description='Record data from the default signal chain')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=5)
    parser.add_argument('--num_rec', required=False, type=int, default=2)
    parser.add_argument('--num_exp', required=False, type=int, default=2)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)
