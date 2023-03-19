import time

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import numpy as np

"""
Test Name: Channel Map Recording 
Test Description: Verify mapped channels are re-ordered/disabled as expected. 
"""

def test(gui, params):

    results = {}

    # Fetch fresh data if needed
    if params['fetch']:

        # Load config for this test
        if params['mode'] == 'local':
            gui.load(params['cfg_path'])

        gui.acquire()
        time.sleep(params['acq_time'])
        gui.record()
        time.sleep(params['rec_time'])

        gui.idle()

    # Validate results
    show = False
    session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

    rec = session.recordnodes[0].recordings[0]
    num_samples,num_channels = rec.continuous[0].samples.shape
    print(f'Num channels: {num_channels} Num samples: {num_samples}')
    testName = "Total channels recorded"
    if num_channels == 12:
      results[testName] = "PASSED"
    else:
      results[testName] = "FAILED\nExpected: %d\nActual: %d" % (12, num_channels)

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
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--address', required=False, type=str, default='http://127.0.0.1')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/channel_map.xml'))
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
