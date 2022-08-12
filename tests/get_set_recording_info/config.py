import platform

os = platform.system()

if os == 'Windows':
    RECORD_PATH = 'C:\\open-ephys\\data'
elif os == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    RECORD_PATH = '<path/to/mac/runner>' #TODO

'''
Test Name: Directory Naming
Test Description: Set the values of prepend, base, and append text fields for record directory naming.
'''

DEBUG_MODE = True
ADDRESS = 'http://127.0.0.1:37497'

ACQUISITION_TIME    = 2 #Number of seconds to acquire data before starting recording (allows for synchronization)
RECORD_TIME         = 5 #Number of seconds to record data between acquistiions
NUM_RECORDINGS      = 1 #Total number of recordings in the experiments
NUM_EXPERIMENTS     = 1 #Total number of experiments

PREPEND_TEXT        = 'prepend' #Text to prepend to the beginning of the experiment name
BASE_TEXT           = 'base' #Text to describe the experiment name
APPEND_TEXT         = 'append' #Text to append to the end of the experiment name

test_params = dict(
    fetch = True, # True to fetch new data and re-run test, False to just show most recent test results 
    address = ADDRESS, 
    acq_time = ACQUISITION_TIME,
    rec_time = RECORD_TIME,
    num_rec = NUM_RECORDINGS,
    num_exp = NUM_EXPERIMENTS,
    prepend_text = PREPEND_TEXT,
    base_text = BASE_TEXT,
    append_text = APPEND_TEXT,
    parent_directory = RECORD_PATH,
)