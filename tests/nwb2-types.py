import time
import os

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

FILE_READER_PATH = "/Volumes/T7/open-ephys/test-suite/input/PridaLabRhythmDataResults/2023-01-26_14-50-52/Record Node 103/experiment1/recording1/structure.oebin"

def test(gui, params):

    results = {}
    
    print("Here!")

    if params['fetch']:
        
        gui.clear_signal_chain()

        gui.add_processor("File Reader")

        #gui.set_file_path(gui.get_processors("File Reader")[0]['id'], "file=" + FILE_READER_PATH)
        gui.set_processor_parameter(gui.get_processors("File Reader")[0]['id'], 'selected_file', FILE_READER_PATH)

        gui.add_processor("Record Node")

        gui.set_record_path(gui.get_processors("Record Node")[0]['id'], params['parent_directory'])

        gui.set_processor_parameter(gui.get_processors("Record Node")[0]['id'], 'engine', 1)

        gui.acquire()

        time.sleep(params['acq_time'])

        gui.record()

        time.sleep(params['rec_time'])

        gui.idle()

        time.sleep(1)

        gui.quit()

        time.sleep(2)

    # Validate
    for path in gui.get_latest_recordings(params['parent_directory']): 

        session = Session(path)

        show = True

        for idx, node in enumerate(session.recordnodes):

            # Check total number of recordings
            testName = 'Total number of recordings'

            condition = len(node.recordings) == params['num_rec']*params['num_exp']
            if condition: results[testName] = "PASSED"
            else: results[testName] = "FAILED\n\tExpected number of recordings: %d actual: %d" % (params['num_rec']*params['num_exp'], len(node.recordings))

            for rec_idx, recording in enumerate(node.recordings):

                for stream_idx, stream in enumerate(recording.continuous):
                            
                    testName = str(recording.format) + " sample count"
                    SAMPLE_NUM_TOLERANCE = 0.2 * stream.metadata['sample_rate']

                    actual = len(stream.timestamps)
                    expected = int(params['rec_time']*stream.metadata['sample_rate'])

                    condition = np.absolute(actual - expected) < SAMPLE_NUM_TOLERANCE
                    if condition: results[testName] = "PASSED"
                    else: results[testName] = "FAILED\n\tExpected number of samples %d != %d" % (actual, expected)

                    if show:

                        import matplotlib.pyplot as plt

                        fig = plt.figure(1)
                        fig.suptitle(recording.format, fontsize=12)
                        ax = fig.add_subplot(params['num_exp'], params['num_rec'], rec_idx+1)
                        ax.plot(stream.timestamps, stream.samples[:,0])
                        ax.set_xlabel('Time [s]')

                        plt.show()

    return results

    # show event data
    #print(tabulate(recording.events, headers='keys')) #tablefmt='psql'))

    #print(tabulate(recording.messages, headers='keys')) #tablefmt='psql')

    # print(recording.spikes[0].timestamps)
    #TODO show spike data


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

    parser = argparse.ArgumentParser(description='Record and load data in all supported formats round trip')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=1)
    parser.add_argument('--rec_time', required=False, type=int, default=1)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=1)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    os.system("rm -rf " + RECORD_PATH + "/*")

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)