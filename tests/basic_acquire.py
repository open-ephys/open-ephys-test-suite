from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import time 

def test(gui, params):

    results = {}

    if params['fetch']:

        gui.clear_signal_chain()

        gui.add_processor('File Reader')

        testName = 'Start acquisition'

        gui.acquire()
        time.sleep(params['acq_time'])

        if gui.status() == 'ACQUIRE':
            results[testName] = "PASSED"
        else:
            results[testName] = "FAILED\n\tGUI returned mode: " + gui.status() + " expected: ACQUIRE"

        testName = 'Stop acquisition'

        gui.idle()
        time.sleep(1)

        if gui.status() == 'IDLE':
            results[testName] = "PASSED"
        else:
            results[testName] = "FAILED\n\tGUI returned mode: " + gui.status() + " expected: IDLE"

        gui.clear_signal_chain()

    return results

'''
================================================================================================================================================
'''
import sys
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default='C:\\open-ephys\\data')
    parser.add_argument('--acq_time', required=False, type=int, default=2)

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)