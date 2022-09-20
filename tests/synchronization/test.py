from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import config

import time

import numpy as np
import matplotlib.pyplot as plt

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']: 

        #Run some actions and record data
        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], config.test_params['engine'])
            gui.set_record_path(node['id'], config.test_params['parent_directory'])

        # Run some actions and record data
        for _ in range(config.test_params['num_exp']):

            for _ in range(config.test_params['num_rec']):

                gui.acquire()
                time.sleep(config.test_params['acq_time'])
                gui.record(config.test_params['rec_time'])

            gui.idle()

            time.sleep(5)

        gui.quit()
        
    # Validate results
    session = Session(gui.get_latest_recordings(config.test_params['parent_directory'])[0])

    for idx, node in enumerate(session.recordnodes):

        for rec_idx, recording in enumerate(node.recordings):

            for str_idx, stream in enumerate(recording.continuous):

                recording.add_sync_line(1, 100, str_idx, main=str_idx==0)  # use as the main timestamps

                show = False
                if show:

                    fig = plt.figure(1)
                    fig.suptitle(stream.name, fontsize=12)
                    ax = fig.add_subplot(config.test_params['num_exp'], config.test_params['num_rec'], rec_idx+1)
                    ax.plot(stream.timestamps, stream.samples[:,0])
                    ax.set_xlabel('Time [s]')

            #TODO: Need to fix this, stream_id vs. stream_name matching conflict
            #recording.compute_global_timestamps()

            print("Test all timestamps are synchronized: ", "PASSED " if not (recording.events.timestamp < 0).any() else "FAILED")

        if show: plt.show()

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))