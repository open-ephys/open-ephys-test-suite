from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import numpy as np
import matplotlib.pyplot as plt

import config
import time
import os

import numpy as np

def test(gui):

    #TODO: Should be able to fetch all available engines via HTTPServer.get_engines()
    RECORD_ENGINES = ("BINARY", "NWB2", "OPEN EPHYS")

    if config.test_params['fetch']:

        file_reader = gui.get_processors("File Reader")[0]

        for idx, engine in enumerate(RECORD_ENGINES):

            for node in gui.get_processors("Record Node"):
                config.test_params['engine'] = "engine=" + str(idx)
                gui.set_record_engine(node['id'], config.test_params['engine'])
                gui.set_record_path(node['id'], config.test_params['parent_directory'])

                if engine == 'NWB2': break

            for _ in range(config.test_params['num_exp']):

                for _ in range(config.test_params['num_rec']):

                    gui.acquire()
                    time.sleep(config.test_params['acq_time'])
                    gui.record(config.test_params['rec_time'])

                gui.idle()
                time.sleep(2)

            path = gui.get_latest_recordings(config.test_params['parent_directory'])[0]
            
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

    for path in gui.get_latest_recordings(config.test_params['parent_directory'], len(RECORD_ENGINES)): 

        print("Validating {}:".format(path))

        session = Session(path) 

        for idx, node in enumerate(session.recordnodes):

            print("Found node: {}".format(idx))

            print("\tExpected number of recordings: {}".format("PASSED" if len(node.recordings) == config.test_params['num_rec']*config.test_params['num_exp'] else "FAILED"))

            for rec_idx, recording in enumerate(node.recordings):

                print("\tFound recording {}".format(rec_idx))

                for str_idx, stream in enumerate(recording.continuous):

                    print("\tFound new stream w/ format {}".format(recording.format))

                    '''
                    SAMPLE_NUM_TOLERANCE = 0.1 * stream.metadata['sample_rate']

                    if np.absolute(len(stream.timestamps) - config.test_params['rec_time']*stream.metadata['sample_rate']) < SAMPLE_NUM_TOLERANCE:
                        print("\t\tData size test PASSED!")
                    else:
                        print("\t\tData size test FAILED! {} != {}".format(len(stream.timestamps), config.test_params['rec_time']*stream.metadata['sample_rate']))
                    '''
                    show = False
                    if show:

                        fig = plt.figure(1)
                        fig.suptitle(stream.name, fontsize=12)
                        ax = fig.add_subplot(config.test_params['num_exp'], config.test_params['num_rec'], rec_idx+1)
                        ax.plot(stream.timestamps, stream.samples[:,0])
                        ax.set_xlabel('Time [s]')

            if show: plt.show()

    # show event data
    #print(tabulate(recording.events, headers='keys')) #tablefmt='psql'))

    #print(tabulate(recording.messages, headers='keys')) #tablefmt='psql')

    # print(recording.spikes[0].timestamps)
    #TODO show spike data


if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))