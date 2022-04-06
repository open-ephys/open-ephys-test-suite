import os
import platform
import subprocess
import signal
import shutil
import argparse

import requests
import json
import time 

import glob
import sys


## Init methods

# Load a configuration file to test
def load(par):
    payload ={ 'path' : par['cfg_path'] }
    url = par['address'] + '/api/load'
    requests.put(url, data = json.dumps(payload))
    time.sleep(1)

# Launch the configured GUI
def launch(par):
    if platform.system() == 'Windows':
        p = subprocess.Popen([par['gui_dir']])
    else:
        p = subprocess.Popen(par['gui_dir'] + 'open-ephys', shell=False, preexec_fn=os.setsid)

# Connect to the HTTPServer
def connect(par):
    print("Attempting to connect to OpenEphys instance on " + par['address'])
    r = requests.get(par['address'])
    print("Connected to OpenEphys instance on " + par['address'])

# Get a list of processors in the current signal chain
def get_processors(par, filter_by_name=""):
    resp = requests.get(par['address'] + '/api/processors')
    data = resp.json()
    if not filter_by_name:
        return data['processors']
    else:
        filtered = []
        for pi in data['processors']:
            for key, value in pi.items():
                print(key, " -- ", value)
            if pi['name'] == filter_by_name:
                filtered.append(pi)
                print("Adding ", filter_by_name)
        return filtered

# General sequence to launch and connect to a GUI configuration
def init(par):

    launch(par)
    connect(par)
    load(par)

## Test methods

# Set path to experiment to load for FileReader at node id
def set_file_path(par, id):
    payload ={ 'text' : par['file_path'] }
    url = par['address'] + '/api/processors/' + str(id) + '/config'
    requests.put(url, data = json.dumps(payload))
    time.sleep(1)

# Set path to recording to load for FileReader at node id
def set_file_index(par, id):
    payload = { 'text' : par['index'] }
    url = par['address'] + '/api/processors/' + str(id) + '/config'
    requests.put(url, data = json.dumps(payload))
    time.sleep(1)

# Set record engine idx for RecordNode at node id
def set_record_engine(par, id):
    payload = { 'text' : par['engine'] }
    url = par['address'] + '/api/processors/' + str(id) + '/config'
    requests.put(url, data = json.dumps(payload))
    time.sleep(1) 

# Acquire data 
def acquire(par):
    payload = { 
        'mode' : 'ACQUIRE',
        'data_parent_dir' : par['rec_dir'] }
    url = '/api/status'
    requests.put(par['address'] + url, data = json.dumps(payload))
    print("Starting acquisition...")
    time.sleep(par['acq_time'])

# Record data
def record(par):
    payload = { 
        'mode' : 'RECORD',
        'data_parent_dir' : par['rec_dir']
    }
    url = '/api/status'
    requests.put(par['address'] + url, data = json.dumps(payload))
    print("Starting recording...")
    time.sleep(par['rec_time'])

# Idle (stops acquisition and recording)
def idle(par):
    payload = { 
        'mode' : 'IDLE',
        'data_parent_dir' : par['rec_dir'] }
    url = '/api/status'
    requests.put(par['address'] + url, data = json.dumps(payload))


## Exit methods

# Quit the GUI 
def exit(par):
    payload = { 'command' : 'quit' }
    url = par['address'] + '/api/window'
    requests.put(url, data = json.dumps(payload))
    print("Quiting GUI...")
    time.sleep(1)


## Run the test

def main(par):

    if par['fetch']:

        try:

            init(par)

            time.sleep(2) #TODO should get signal back from GUI that it's ready for acquisition

            #all_processors = get_processors(par)

            record_nodes = get_processors(par, "Record Node")

            for node in record_nodes:
                set_record_engine(par, node['id']) #what if a record engine not installed yet?
                break;

            NUM_RECORDINGS = par['num_rec']
            for i in range(NUM_RECORDINGS):

                acquire(par)

                record(par)

                idle(par)

            exit(par)

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print("Timeout")
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print("Bad URL")
        except requests.exceptions.RequestException as e:
            # OpenEphys server needs to be enabled
            print("OpenEphys HttpServer likely not enabled")
            raise SystemExit(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true', default=False) #
    parser.add_argument('--address', required=False, default='http://127.0.0.1:37497')
    parser.add_argument('--cfg_path', required=False, default='C:\\Users\\Pavel\\Projects\\Allen\\OpenEphys\\configs\\test_config.xml')   
    parser.add_argument('--gui_dir', required=False, default='C:\\Users\\Pavel\\Projects\\Allen\\OpenEphys\\plugin-GUI\\Build\\Debug\\open-ephys.exe') #/home/pavel/Projects/Allen/OpenEphys/plugin-GUI/Build/Release/')
    parser.add_argument('--rec_dir', required=False, default='C:\\Users\\Pavel\\OneDrive\\Documents\\Open Ephys')
    parser.add_argument('--file_path', required=False, default='file=/home/pavel/Projects/Allen/OpenEphys/plugin-GUI/Resources/DataFiles/structure.oebin')
    parser.add_argument('--index', required=False, default='index=0')
    parser.add_argument('--engine', required=False, default='engine=0')
    parser.add_argument('--acq_time', required=False, default=2)
    parser.add_argument('--rec_time', required=False, default=2)
    parser.add_argument('--num_rec', required=False, default=1)
    parser.add_argument('--quit', required=False, default='quit')

    par__main=vars(parser.parse_args(sys.argv[1:]))
    main(par__main)

'''
python test_record.py --fetch
'''