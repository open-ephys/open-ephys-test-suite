from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import numpy as np

import time
import os

import numpy as np

def test(gui, params):

    results = {}

    RECORD_ENGINES = ("BINARY", "NWB2", "OPEN EPHYS")

    if params['fetch']:

        # Load config for this test
        if params['mode'] == 'local':
            gui.load(params['cfg_path'])

        file_reader = gui.get_processors("File Reader")[0]

        for idx, engine in enumerate(RECORD_ENGINES):

            for node in gui.get_processors("Record Node"):
                params['engine'] = "engine=" + str(idx)
                gui.set_record_engine(node['id'], params['engine'])
                gui.set_record_path(node['id'], params['parent_directory'])

                if engine == 'NWB2': break

            for _ in range(params['num_exp']):

                for _ in range(params['num_rec']):

                    gui.acquire()
                    time.sleep(params['acq_time'])
                    gui.record()
                    time.sleep(params['rec_time'])

                gui.idle()
                time.sleep(2)

            path = gui.get_latest_recordings(params['parent_directory'])[0]
            
            if engine != 'NWB2':

                session = Session(path)

                for idx, node in enumerate(session.recordnodes):

                    path = node.recordings[0].directory

                    if node.format == 'binary':
                        data_path = os.path.join(path, 'structure.oebin')
                    elif node.format == 'open-ephys':
                        data_path = os.path.join(path, 'structure.openephys')

                    break

            else:

                data_path = os.path.join(path, "Record Node 101", "experiment1.nwb")

            #Set File Reader to read from the last recorded data path
            gui.set_file_path(file_reader['id'], "file=" + data_path)

        gui.quit()

        time.sleep(4)

    # Validate

    for path in gui.get_latest_recordings(params['parent_directory'], len(RECORD_ENGINES)): 

        session = Session(path) 

        for idx, node in enumerate(session.recordnodes):

            # Check total number of recordings
            testName = 'Total number of recordings'
            if params['num_rec']*params['num_exp'] == len(node.recordings):
                results[testName] = "PASSED"
            else:
                results[testName] = "FAILED\n\tExpected number of recordings: {} actual: {}" % (params['num_rec']*params['num_exp'], len(node.recordings))

            for rec_idx, recording in enumerate(node.recordings):

                for str_idx, stream in enumerate(recording.continuous):
                            
                    testName = str(recording.format) + " sample count"
                    SAMPLE_NUM_TOLERANCE = 0.1 * stream.metadata['sample_rate']

                    if np.absolute(len(stream.timestamps) - params['rec_time']*stream.metadata['sample_rate']) < SAMPLE_NUM_TOLERANCE:
                        results[testName] = "PASSED"
                    else:
                        results[testName] = "FAILED\n\tExpected number of samples {} != {}" % (len(stream.timestamps), params['rec_time']*stream.metadata['sample_rate'])

                    show = False
                    if show:

                        import matplotlib.pyplot as plt

                        fig = plt.figure(1)
                        fig.suptitle(stream.name, fontsize=12)
                        ax = fig.add_subplot(params['num_exp'], params['num_rec'], rec_idx+1)
                        ax.plot(stream.timestamps, stream.samples[:,0])
                        ax.set_xlabel('Time [s]')

            if show: plt.show()

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
    RECORD_PATH = 'C:\\open-ephys\\data'
elif platform.system() == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    RECORD_PATH = '<path/to/mac/runner>' #TODO

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=False, default=False)
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