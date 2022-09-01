from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import config

def test(gui):

    # Fetch fresh data if needed
    if config.test_params['fetch']: 

        gui.set_prepend_text(config.test_params['prepend_text'])
        gui.set_base_text(config.test_params['base_text'])
        gui.set_append_text(config.test_params['append_text'])
        gui.set_parent_dir(config.test_params['parent_directory'])

        print("Test prepend text: ", "PASSED" if gui.get_recording_info('prepend_text') == config.test_params['prepend_text'] else "FAILED")
        print("Test base text: ", "PASSED" if gui.get_recording_info('base_text') == config.test_params['base_text'] else "FAILED")
        print("Test append text: ", "PASSED" if gui.get_recording_info('append_text') == config.test_params['append_text'] else "FAILED")
        if gui.get_recording_info('parent_directory') == config.test_params['parent_directory']:
            print("Test parent dir: ", "PASSED")
        else:
            print("Test parent dir: ", "FAILED    Got parent_directory: ", gui.get_recording_info('parent_directory'), " Expected parent_directory: ", config.test_params['parent_directory'])

        #TODO: Record data and then check that the recorded folder has the desired directory name:

        gui.quit()

    # Validate results
    
    #TODO: Parse recorded data folder name and confirm that it matches the desired name
    #session = Session(gui.get_latest_recordings(config.test_params['parent_directory'])[0])

if __name__ == '__main__':
    test(OpenEphysHTTPServer(config.test_params['address']))