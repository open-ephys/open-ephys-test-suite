import time

from open_ephys.control import OpenEphysHTTPServer

"""
Test Name: Minimal Acquisition
Test Description: Confirm the GUI can start and stop data acquisition
"""

def test(gui, params):

    results = {}

    gui.clear_signal_chain()

    gui.add_processor('File Reader')

    gui.acquire()
    time.sleep(params['acq_time'])

    testName = 'Start acquisition'
    condition = gui.status() == 'ACQUIRE'
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tGUI returned mode: " + gui.status() + " expected: ACQUIRE"

    gui.idle()
    time.sleep(1)

    testName = 'Stop acquisition'
    condition = gui.status() == 'IDLE'
    if condition: results[testName] = "PASSED"
    else: results[testName] = "FAILED\n\tGUI returned mode: " + gui.status() + " expected: IDLE"

    gui.clear_signal_chain()

    return results

'''
================================================================================================================================================
'''
import sys
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Acquire data from the default signal chain')
    parser.add_argument('--acq_time', required=False, type=int, default=2)

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)