import time

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

"""
Test Name: Audio Device Test
Test Description: Configures the buffer size and sample rate of the audio device and validates recordings
"""

def test(gui, params):

    results = {}

    if params['fetch']:

        #Attempt to change the buffer size and sample rate during acquisition

        gui.clear_signal_chain()
        gui.add_processor("File Reader")
        gui.add_processor("Record Node")

        test_name = 'Prevent buffer size change during acquisition'

        gui.acquire()

        original_buffer_size = gui.get_audio_settings('buffer_size')
        gui.set_buffer_size(512)
        time.sleep(1)
        new_buffer_size = gui.get_audio_settings('buffer_size')

        if new_buffer_size != original_buffer_size:
            results[test_name] = "FAILED\n\tExpected: %d\n\tActual: %d" % (original_buffer_size, new_buffer_size)
        else:
            results[test_name] = "PASSED"

        test_name = 'Prevent sample rate change during acquisition'

        original_sample_rate = gui.get_audio_settings('sample_rate')
        gui.set_sample_rate(48000)
        time.sleep(1)
        new_sample_rate = gui.get_audio_settings('sample_rate')

        if new_sample_rate != original_sample_rate:
            results[test_name] = "FAILED\n\tExpected: %d\n\tActual: %d" % (original_sample_rate, new_sample_rate)
        else:
            results[test_name] = "PASSED"

        gui.idle()

        #Record data with various buffer sizes and sample rates
        BUFFER_SIZES = [512, 1024]#, 2048, 4096]
        SAMPLE_RATES = [44100, 48000]#, 88200, 96000]

        for buffer_size in BUFFER_SIZES:

            for sample_rate in SAMPLE_RATES:

                gui.set_buffer_size(buffer_size)
                gui.set_sample_rate(sample_rate)

                for _ in range(params['num_exp']):

                    for _ in range(params['num_rec']):

                        gui.acquire()
                        time.sleep(params['acq_time'])
                        gui.record()
                        time.sleep(params['rec_time'])

                    gui.idle()

                # Validate results
                session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

                for node_idx, node in enumerate(session.recordnodes):

                    for rec_idx, recording in enumerate(node.recordings):

                        for str_idx, stream in enumerate(recording.continuous):

                            SAMPLE_RATE = stream.metadata['sample_rate']

                            SAMPLE_NUM_TOLERANCE = 0.1 * SAMPLE_RATE

                            testName = "Recording %d length" % (rec_idx+1)

                            if abs(stream.samples.shape[0] - SAMPLE_RATE * params['rec_time']) < SAMPLE_NUM_TOLERANCE:
                                results[testName] = "PASSED"
                            else:
                                results[testName] = "FAILED\nExpected: %d\nActual: %d" % (SAMPLE_RATE * params['rec_time'], stream.data.shape[0])
        

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
    parser.add_argument('--fetch', required=False, type=int, default=1)
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