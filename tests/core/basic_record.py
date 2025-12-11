import time
import traceback
import sys

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

def log(msg):
    print(f'[basic_record] {msg}', flush=True)

"""
Test Name: Minimal Recording
Test Description: Record and check data from the default signal chain
"""

def test(gui, params):

    results = {}

    try:
        # Fetch fresh data if needed
        if params['fetch']:
            log("Starting data fetch phase")
            
            try:
                # Load config for this test
                log(f"Loading config from: {params['cfg_path']}")
                gui.load(params['cfg_path'])
                log("Config loaded successfully")
            except Exception as e:
                log(f"ERROR loading config: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

            try:
                # Apply custom data recording parameters
                log("Setting up record nodes")
                record_nodes = gui.get_processors("Record Node")
                log(f"Found {len(record_nodes)} record node(s)")
                for node in record_nodes:
                    log(f"Configuring record node {node['id']}")
                    gui.set_record_engine(node['id'], params['engine'])
                    gui.set_record_path(node['id'], params['parent_directory'])
                log("Record nodes configured successfully")
            except Exception as e:
                log(f"ERROR configuring record nodes: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

            try:
                # Run some actions and record data
                log(f"Starting acquisition/recording loop: {params['num_exp']} experiments, {params['num_rec']} recordings each")
                for exp_idx in range(params['num_exp']):
                    log(f"Experiment {exp_idx+1}/{params['num_exp']}")
                    for rec_idx in range(params['num_rec']):
                        log(f"  Recording {rec_idx+1}/{params['num_rec']}")
                        gui.acquire()
                        time.sleep(params['acq_time'])
                        gui.record()
                        time.sleep(params['rec_time'])
                    gui.idle()
                log("Acquisition/recording phase completed")
            except Exception as e:
                log(f"ERROR during acquisition/recording: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

        # Validate results
        try:
            log("Starting validation phase")
            dir_ = params['parent_directory']
            log(f"Parent directory: {dir_}")
            
            try:
                latest_recordings = gui.get_latest_recordings(dir_)
                log(f"Found {len(latest_recordings)} latest recording(s)")
                if len(latest_recordings) == 0:
                    raise ValueError(f"No recordings found in {dir_}")
                session = Session(latest_recordings[0])
                log(f"Session loaded: {len(session.recordnodes)} record node(s)")
            except Exception as e:
                log(f"ERROR loading session: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

            for node_idx, node in enumerate(session.recordnodes):
                log(f"Processing record node {node_idx}: {len(node.recordings)} recording(s)")

                # Validate total number of recordings
                testName = "Total recordings"
                condition = len(node.recordings) == params['num_rec']*params['num_exp']
                if condition: results[testName] = "PASSED"
                else: results[testName] = "FAILED\nExpected: %d\nActual: %d" % (params['num_rec']*params['num_exp'], len(node.recordings))

                for rec_idx, recording in enumerate(node.recordings):
                    log(f"  Processing recording {rec_idx+1}: {len(recording.continuous)} continuous stream(s)")

                    for _, stream in enumerate(recording.continuous):

                        # Validate amount of continuous data recorded is within range
                        testName = f"Recording {rec_idx+1} data size"
                        expected_samples = params['rec_time'] * stream.metadata.sample_rate
                        condition = np.isclose(len(stream.timestamps), expected_samples, atol=0.05 * expected_samples)
                        if condition: results[testName] = "PASSED"
                        else: results[testName] = "FAILED\nExpected: %d\nActual: %d" % (expected_samples, len(stream.timestamps))

                        # Validate spikes were written in the second record node
                        testName = f"Recording {rec_idx+1} spike count"
                        condition = node_idx  == 1 and len(recording.spikes) > 0
                        if condition: results[testName] = "PASSED"
                        else: results[testName] = "FAILED\nExpected: >0\nActual: %d" % len(recording.spikes)

                        # TODO: Save spike data to be used to verify channel mapper downstream.
                        # for spike_channel in recording.spikes:
                        #     print(f"{spike_channel.metadata['name']} : {len(spike_channel.sample_numbers)} spikes")
            
            log("Validation phase completed")
        except Exception as e:
            log(f"ERROR during validation: {e}")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            raise

    except Exception as e:
        log(f"FATAL ERROR in test function: {e}")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        raise

    return results


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
    try:
        log("Starting basic_record test")
        
        parser = argparse.ArgumentParser(description='Record data from the default signal chain')
        parser.add_argument('--fetch', required=False, type=int, default=1)
        parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
        parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../../configs/file_reader_config.xml'))
        parser.add_argument('--acq_time', required=False, type=int, default=2)
        parser.add_argument('--rec_time', required=False, type=int, default=5)
        parser.add_argument('--num_rec', required=False, type=int, default=2)
        parser.add_argument('--num_exp', required=False, type=int, default=2)
        parser.add_argument('--prepend_text', required=False, type=str, default='')
        parser.add_argument('--base_text', required=False, type=str, default='')
        parser.add_argument('--append_text', required=False, type=str, default='')
        parser.add_argument('--engine', required=False, type=str, default='engine=0')

        params = vars(parser.parse_args(sys.argv[1:]))
        log(f"Test parameters: {params}")

        log("Initializing OpenEphysHTTPServer")
        gui = OpenEphysHTTPServer()
        log("OpenEphysHTTPServer initialized")

        log("Calling test function")
        results = test(gui, params)
        log("Test function completed")

        log("Printing results")
        for test, result in results.items():
            print(test, '-'*(80-len(test)), result, flush=True)
        
        log("basic_record test completed successfully")
        sys.exit(0)
        
    except Exception as e:
        log(f"FATAL ERROR in main: {e}")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)
