from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import numpy as np
import matplotlib.pyplot as plt

import config

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']:

        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], config.test_params['engine'])
            gui.set_record_path(node['id'], config.test_params['parent_directory'])

        # Run some actions and record data
        for _ in range(config.test_params['num_exp']):

            for _ in range(config.test_params['num_rec']):

                gui.acquire(config.test_params['acq_time'])
                gui.record(config.test_params['rec_time'])

            gui.idle()

        gui.quit()

    # Validate results
    show = False
    session = Session(gui.get_latest_recordings(config.test_params['parent_directory'])[0])

    for node_idx, node in enumerate(session.recordnodes):

        # Confirm total number of recordings
        print("Total recordings: {}".format(
            "PASSED" if len(node.recordings) == config.test_params['num_rec']*config.test_params['num_exp'] else "FAILED"))

        for rec_idx, recording in enumerate(node.recordings):

            for str_idx, stream in enumerate(recording.continuous):

                try: 
                    SAMPLE_RATE = stream.metadata['sample_rate'] 
                except:
                    SAMPLE_RATE = 40000 #OpenEphys format does not include sample rate in metadata 

                SAMPLE_NUM_TOLERANCE = 0.1 * SAMPLE_RATE

                if np.absolute(len(stream.timestamps) - config.test_params['rec_time']*SAMPLE_RATE) < SAMPLE_NUM_TOLERANCE:
                    print("Data size test PASSED")
                else:
                    print("Data size test FAILED! {} != {}".format(len(stream.timestamps), config.test_params['rec_time']*stream.metadata['sample_rate']))

                if show:

                    fig = plt.figure(1)
                    fig.suptitle(stream.name, fontsize=12)
                    ax = fig.add_subplot(config.test_params['num_exp'], config.test_params['num_rec'], rec_idx+1)
                    ax.plot(stream.timestamps, stream.samples[:,0])
                    ax.set_xlabel('Time [s]')

        if show: plt.show()

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))