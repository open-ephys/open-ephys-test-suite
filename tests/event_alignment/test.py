from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import config

import time
import numpy as np
import matplotlib.pyplot as plt
import tabulate

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']:

        gui.init(config.test_params['cfg_path'])

        for node in gui.get_processors("Record Node"):
            gui.set_record_engine(node['id'], config.test_params['engine'])
            gui.set_record_path(node['id'], config.test_params['parent_directory'])

        for _ in range(config.test_params['num_exp']):

            for _ in range(config.test_params['num_rec']):

                gui.acquire(config.test_params['acq_time'])
                gui.record(config.test_params['rec_time'])

            gui.idle()

        gui.quit()

    time.sleep(2)

    # Validate
    session = Session(gui.get_latest_recordings(config.test_params['parent_directory'])[0])

    for node in session.recordnodes:

        for rec_idx, recording in enumerate(node.recordings):

            print(recording.events) #tablefmt='psql'))

            #TODO: add more tests

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))