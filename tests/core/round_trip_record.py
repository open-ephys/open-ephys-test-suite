import time
import os

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

def log(msg): print(f'[test-suite] {msg}', flush=True)

def test(gui, params):

    results = {}

    RECORD_ENGINES = {
        "BINARY" : 0,
        "NWB2" : 1,
        "OPENEPHYS" : 2
    }

    if params['fetch']:

        gui.load(params['cfg_path'])

        file_reader = gui.get_processors("File Reader")[0]

        for node in gui.get_processors("Record Node"):
            gui.set_record_path(node['id'], params['parent_directory'])
            #gui.set_processor_parameter(node['id'], 'directory', params['parent_directory'])

        for engine, idx in RECORD_ENGINES.items():

            #gui.set_start_new_dir()

            params['engine'] = 'engine=' + engine

            for node in gui.get_processors("Record Node"):
                log(f"Setting engine {params['engine']} for Record Node {node['id']}")
                #gui.set_record_engine(node['id'], params['engine'])
                gui.set_processor_parameter(node['id'], 'engine', RECORD_ENGINES[engine])

                parameters = gui.get_parameters(node['id'])['parameters']
                engine_param = next((param for param in parameters if param['name'] == 'engine'), None)
                log(f"Engine parameter: {engine_param}")
                if not engine_param['value'] == str(idx):
                    raise Exception(f"Failed to set engine {params['engine']} for Record Node {node['id']}: {engine_param['value']}")

                if engine == 'NWB2': break

            for _ in range(params['num_exp']):

                for _ in range(params['num_rec']):

                    # Start data acquisition
                    gui.acquire()
                    time.sleep(params['acq_time'])
                    # Start recording data
                    gui.record()
                    time.sleep(params['rec_time'])

                # Stop data acquisition
                gui.idle()
                time.sleep(2)

            path = gui.get_latest_recordings(params['parent_directory'])[0]

            print(path)
            
            if engine != 'NWB2': #TODO: Enable multi-threaded recording for NWB

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
            #gui.set_file_path(file_reader['id'], "file=" + data_path) (not implemented in v1.0 yet)
            gui.set_processor_parameter(file_reader['id'], 'selected_file', data_path)

        time.sleep(2)

    # Validate
    for path in gui.get_latest_recordings(params['parent_directory'], len(RECORD_ENGINES)): 

        session = Session(path) 

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

                    show = False
                    if show:

                        import matplotlib.pyplot as plt

                        fig = plt.figure(1)
                        fig.suptitle(recording.format, fontsize=12)
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
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=4)
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