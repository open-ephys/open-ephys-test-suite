import time

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

"""
Test Name: Channel Map Recording 
Test Description: Verify mapped channels are re-ordered/disabled as expected. 
"""
def test(gui, params):

    results = {}

    # Fetch fresh data if needed
    if params['fetch']:

        gui.load(params['cfg_path'])
        
        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], params['engine'])
            gui.set_record_path(node['id'], params['parent_directory'])

        gui.acquire()
        time.sleep(params['acq_time'])
        gui.record()

        time.sleep(params['rec_time'])
        gui.idle()

    # Validate results
    show = False
    session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

    print(session)

    recording = session.recordnodes[1].recordings[0]
    num_samples,num_channels = recording.continuous[0].samples.shape
    print(f'Num channels: {num_channels} Num samples: {num_samples}')

    testName = "Total channels recorded"
    condition = num_channels == 14
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\nExpected: %d\nActual: %d" % (12, num_channels)

    testName = "Spikes recorded"
    condition = len(recording.spikes) > 0
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\nExpected: >0\nActual: %d" % len(recording.spikes)

    for spike_channel in recording.spikes:
        print(f"{spike_channel.metadata['name']} : {len(spike_channel.sample_numbers)} spikes")

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

    parser = argparse.ArgumentParser(description='Test Channel Map Functionality')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/channel_map.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=2)
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
