import time
import traceback
import sys

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

def log(msg):
    print(f'[disabled_streams_record] {msg}', flush=True)

"""
Test Name: Disabled Streams Recording (Two Record Nodes)
Test Description: Record data with two Record Nodes, each having a different subset of
                  streams disabled via channel masking.
                  - Record Node 1: last 2 streams disabled (Probe-C-AP, Probe-D-AP)
                  - Record Node 2: first 2 streams disabled (Probe-A-AP, Probe-B-AP)
                  Stream names, counts, and channel counts are derived dynamically from
                  the /api/processors response. The acquisition/recording cycle is repeated
                  num_recs times: acquire -> wait -> record -> wait -> idle.
"""

N_DISABLED = 2  # streams disabled per Record Node


def test(gui, params):

    results = {}

    try:
        if params['fetch']:
            log("Starting data fetch phase")

            try:
                log(f"Loading config from: {params['cfg_path']}")
                gui.load(params['cfg_path'])
                log("Config loaded successfully")
            except Exception as e:
                log(f"ERROR loading config: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

        # Derive stream info from both record nodes in the live signal chain
        try:
            record_nodes = gui.get_processors("Record Node")
            if len(record_nodes) < 2:
                raise RuntimeError(f"Expected at least 2 Record Nodes, found {len(record_nodes)}")
            rn1_streams = record_nodes[0]['streams']
            rn2_streams = record_nodes[1]['streams']
            num_total_streams = len(rn1_streams)
            log(f"Record Node 1 ({record_nodes[0]['id']}) streams: {[s['name'] for s in rn1_streams]}")
            log(f"Record Node 2 ({record_nodes[1]['id']}) streams: {[s['name'] for s in rn2_streams]}")
        except Exception as e:
            log(f"ERROR reading Record Node stream info: {e}")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            raise

        # RN1: disable last N_DISABLED streams; RN2: disable first N_DISABLED streams
        rn1_disabled_indices = list(range(num_total_streams - N_DISABLED, num_total_streams))
        rn2_disabled_indices = list(range(N_DISABLED))
        rn1_enabled_streams = rn1_streams[:num_total_streams - N_DISABLED]
        rn2_enabled_streams = rn2_streams[N_DISABLED:]
        node_enabled_streams = [rn1_enabled_streams, rn2_enabled_streams]

        log(f"Record Node 1: disabling streams {rn1_disabled_indices} "
            f"({[rn1_streams[i]['name'] for i in rn1_disabled_indices]})")
        log(f"Record Node 2: disabling streams {rn2_disabled_indices} "
            f"({[rn2_streams[i]['name'] for i in rn2_disabled_indices]})")

        if params['fetch']:
            try:
                node_streams_list = [rn1_streams, rn2_streams]
                disabled_indices_list = [rn1_disabled_indices, rn2_disabled_indices]

                for node, node_streams, disabled_indices in zip(
                    record_nodes[:2], node_streams_list, disabled_indices_list
                ):
                    log(f"Configuring record node {node['id']}")
                    gui.set_record_engine(node['id'], params['engine'])
                    gui.set_record_path(node['id'], params['parent_directory'])

                    for stream_idx in disabled_indices:
                        stream_name = node_streams[stream_idx]['name']
                        log(f"  Disabling stream {stream_idx} ({stream_name}) on node {node['id']}")
                        gui.set_stream_parameter(node['id'], stream_idx, 'channels', [])

                log("Record nodes configured successfully")
            except Exception as e:
                log(f"ERROR configuring record nodes: {e}")
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                raise

            try:
                num_recs = params['num_recs']
                log(f"Starting {num_recs} acquisition/recording cycle(s)")
                for rec_idx in range(num_recs):
                    log(f"  Cycle {rec_idx + 1}/{num_recs}: acquiring")
                    gui.acquire()
                    time.sleep(params['acq_time'])
                    log(f"  Cycle {rec_idx + 1}/{num_recs}: recording")
                    gui.record()
                    time.sleep(params['rec_time'])
                    log(f"  Cycle {rec_idx + 1}/{num_recs}: stopping")
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

            latest_recordings = gui.get_latest_recordings(dir_)
            log(f"Found {len(latest_recordings)} latest recording(s)")
            if len(latest_recordings) == 0:
                raise ValueError(f"No recordings found in {dir_}")

            session = Session(latest_recordings[0])
            log(f"Session loaded: {len(session.recordnodes)} record node(s)")

            num_recs = params['num_recs']
            for node_idx, node in enumerate(session.recordnodes):
                enabled_streams_info = node_enabled_streams[node_idx] if node_idx < len(node_enabled_streams) else []
                num_enabled = len(enabled_streams_info)
                log(f"Processing record node {node_idx}: {len(node.recordings)} recording(s), "
                    f"expecting {num_enabled} enabled stream(s) per recording")

                testName = f"Node {node_idx} recording count"
                if len(node.recordings) == num_recs:
                    results[testName] = "PASSED"
                else:
                    results[testName] = "FAILED\nExpected: %d\nActual: %d" % (num_recs, len(node.recordings))

                for rec_idx, recording in enumerate(node.recordings):
                    num_streams_recorded = len(recording.continuous)

                    testName = f"Node {node_idx} recording {rec_idx + 1} active stream count"
                    if num_streams_recorded == num_enabled:
                        results[testName] = "PASSED"
                    else:
                        results[testName] = "FAILED\nExpected: %d\nActual: %d" % (num_enabled, num_streams_recorded)

                    for stream_idx, stream in enumerate(recording.continuous):
                        if stream_idx >= len(enabled_streams_info):
                            log(f"WARNING: More streams recorded than expected. "
                                f"Stream idx: {stream_idx}, info length: {len(enabled_streams_info)}")
                            continue

                        num_samples, num_channels = stream.samples.shape
                        expected_samples = int(params['rec_time'] * stream.metadata.sample_rate)
                        expected_channels = enabled_streams_info[stream_idx]['channel_count']
                        expected_stream_name = enabled_streams_info[stream_idx]['name']
                        actual_stream_name = stream.metadata.stream_name

                        testName = f"Node {node_idx} recording {rec_idx + 1} stream {stream_idx} name"
                        if actual_stream_name == expected_stream_name:
                            results[testName] = "PASSED"
                        else:
                            results[testName] = "FAILED\nExpected: {}\nActual: {}".format(
                                expected_stream_name, actual_stream_name)
                            continue

                        testName = f"Node {node_idx} recording {rec_idx + 1} stream '{expected_stream_name}' sample count"
                        condition = np.isclose(num_samples, expected_samples, atol=0.05 * expected_samples)
                        if condition:
                            results[testName] = "PASSED"
                        else:
                            results[testName] = "FAILED\nExpected: ~%d\nActual: %d" % (expected_samples, num_samples)

                        testName = f"Node {node_idx} recording {rec_idx + 1} stream '{expected_stream_name}' channel count"
                        if num_channels == expected_channels:
                            results[testName] = "PASSED"
                        else:
                            results[testName] = "FAILED\nExpected: %d\nActual: %d" % (expected_channels, num_channels)

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
import argparse
import platform

from pathlib import Path

if platform.system() == 'Windows':
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_WINDOWS_GITHUB_RECORD_PATH')
    else:
        RECORD_PATH = os.getenv('OE_WINDOWS_LOCAL_RECORD_PATH')
elif platform.system() == 'Linux':
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_LINUX_GITHUB_RECORD_PATH')
    else:
        RECORD_PATH = os.getenv('OE_LINUX_LOCAL_RECORD_PATH')
else:
    if os.getenv("GITHUB_ACTIONS"):
        RECORD_PATH = os.getenv('OE_MAC_GITHUB_RECORD_PATH')
    else:
        RECORD_PATH = os.getenv('OE_MAC_LOCAL_RECORD_PATH')

if (not RECORD_PATH):
    RECORD_PATH = "None"

if __name__ == '__main__':
    try:
        log("Starting disabled_streams_record test")

        parser = argparse.ArgumentParser(description='Test recording with disabled streams on Record Node')
        parser.add_argument('--fetch', required=False, type=int, default=1)
        parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
        parser.add_argument('--cfg_path', required=False, type=str,
                            default=os.path.join(Path(__file__).resolve().parent,
                                                 '../../configs/source_sim.xml'))
        parser.add_argument('--acq_time', required=False, type=int, default=8)
        parser.add_argument('--rec_time', required=False, type=int, default=5)
        parser.add_argument('--num_recs', required=False, type=int, default=3,
                            help='Number of acquire/record/idle cycles to run')
        parser.add_argument('--engine', required=False, type=str, default="0", help='Record engine index to use for recording')

        params = vars(parser.parse_args(sys.argv[1:]))
        log(f"Test parameters: {params}")

        log("Initializing OpenEphysHTTPServer")
        gui = OpenEphysHTTPServer()
        log("OpenEphysHTTPServer initialized")

        log("Calling test function")
        results = test(gui, params)
        log("Test function completed")

        log("Printing results")
        for test_name, result in results.items():
            print(test_name, '-' * (80 - len(test_name)), result, flush=True)

        log("disabled_streams_record test completed")
        sys.exit(0)

    except Exception as e:
        log(f"UNHANDLED EXCEPTION: {e}")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)
