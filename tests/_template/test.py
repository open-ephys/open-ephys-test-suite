from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import config

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']: 

        #Run some actions and record data
        
        gui.quit()

    # Validate results
    # session = Session(gui.get_latest_recordings(config.test_params['parent_directory'])[0])

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))