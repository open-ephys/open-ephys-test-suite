from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import config

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']:

        bandpass_filter = gui.get_processors("Bandpass Filter")[0]
        gui.set_param(bandpass_filter['id'], 0, 'low_cut', 350.0)
        bandpass_filter = gui.get_processors("Bandpass Filter")[0]

        for param in bandpass_filter["streams"][0]["parameters"]:
            if param["name"] == 'low_cut':
                print("Set param test: {}".format("PASSED" if float(param["value"]) == 350 else "FAILED!"))
                break
                
        gui.quit()

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))