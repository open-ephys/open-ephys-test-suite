import time
import psutil

import numpy as np

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

"""
Test Name: Audio Device Test
Test Description: Configures available audio devices and validates recordings
"""

def test(gui, params):

    results = {}

    if params['fetch']:

        testName = 'Has available audio device'

        available_audio_devices = gui.get_audio_devices()

        condition = len(available_audio_devices) > 0
        if condition: results[testName] = "PASSED"
        else: results[testName] = "FAILED\n\tNo audio devices found"

        testName = 'Get audio device settings'

        audio_settings = gui.get_audio_settings()

        available_buffer_sizes = audio_settings['available_buffer_sizes']
        available_sample_rates = audio_settings['available_sample_rates']

        device_type = audio_settings['device_type']
        device_name = audio_settings['device_name']
        buffer_size = audio_settings['buffer_size']
        sample_rate = audio_settings['sample_rate']

        #print("Current device type: %s" % device_type)
        #print("Current device name: %s" % device_name)
        #print("Current buffer size: %d" % buffer_size)
        #print("Current sample rate: %d" % sample_rate)

        gui.clear_signal_chain()
        gui.add_processor("File Reader")
        gui.add_processor("Record Node")

        record_node = gui.get_processors("Record Node")[0]
        gui.set_record_engine(record_node['id'], params['engine'])
        gui.set_record_path(record_node['id'], params['parent_directory'])

        test_name = 'Prevent buffer size change during acquisition'

        gui.acquire()

        original_buffer_size = gui.get_audio_settings('buffer_size')
        gui.set_buffer_size(available_buffer_sizes[-1])
        new_buffer_size = gui.get_audio_settings('buffer_size')

        condition = new_buffer_size == original_buffer_size
        if condition: results[test_name] = "PASSED"
        else: results[test_name] = "FAILED\n\tExpected: %d\n\tActual: %d" % (original_buffer_size, new_buffer_size)

        test_name = 'Prevent sample rate change during acquisition'

        original_sample_rate = gui.get_audio_settings('sample_rate')
        gui.set_sample_rate(available_sample_rates[0])
        new_sample_rate = gui.get_audio_settings('sample_rate')

        condition = new_sample_rate == original_sample_rate
        if condition: results[test_name] = "PASSED"
        else: results[test_name] = "FAILED\n\tExpected: %d\n\tActual: %d" % (original_sample_rate, new_sample_rate)

        gui.idle()

        #Record data with min and max available buffer sizes and sample rates
        BUFFER_SIZES = [available_buffer_sizes[0], available_buffer_sizes[-1]]
        SAMPLE_RATES = [available_sample_rates[0], available_sample_rates[-1]]

        #Test current audio device min and max settings
        #TODO: Iterate over all available audio API types and devices
        #gui.set_device_type('Core Audio')
        #gui.set_device_name('Scarlett 2i4 USB')
        record_count = 0

        for buffer_size in BUFFER_SIZES:

            gui.set_buffer_size(buffer_size)

            for sample_rate in SAMPLE_RATES:

                gui.set_sample_rate(sample_rate)

                for _ in range(params['num_exp']):

                    for _ in range(params['num_rec']):

                        gui.acquire()
                        ps_acquire_cpu = psutil.cpu_percent(interval=params['acq_time'])
                        gui_acquire_cpu = gui.get_cpu_usage()
                        latency_acquire = gui.get_latencies()

                        gui.record()
                        ps_record_cpu = psutil.cpu_percent(interval=params['rec_time'])
                        gui_record_cpu = gui.get_cpu_usage()
                        latency_record = gui.get_latencies()

                    gui.idle()

                    time.sleep(1)

                # Validate results
                session = Session(gui.get_latest_recordings(params['parent_directory'])[0])

                for _, node in enumerate(session.recordnodes):

                    latest_recording = node.recordings[-1]

                    for _, stream in enumerate(latest_recording.continuous):

                        SAMPLE_RATE = stream.metadata.sample_rate

                        SAMPLE_NUM_TOLERANCE = 0.025 * SAMPLE_RATE*params['rec_time']

                        testName = f"Recording w/ buffer size {buffer_size} sample rate {sample_rate}"
                        stats = f"% GUI CPU: Acquire {100 * float(gui_acquire_cpu['usage']):.1f} Record {100 * float(gui_record_cpu['usage']):.1f}\n"
                        stats += f"% PS CPU: Acquire {ps_acquire_cpu:.1f} Record {ps_record_cpu:.1f}\n"
                        stats += f"Latency: Acquire\n"
                        for processor in latency_acquire['processors']:
                            stats += f"\t{processor['name']}: {processor['id']}\n"
                            for data_stream in processor['streams']:
                                stats += f"\t\t{data_stream['name']}: {1000*data_stream['latency']:.1f} us\n"
                        stats += f"Latency: Record\n"
                        for processor in latency_record['processors']:
                            stats += f"\t{processor['name']}: {processor['id']}\n"
                            for data_stream in processor['streams']:
                                stats += f"\t\t{data_stream['name']}: {1000*data_stream['latency']:.1f} us\n"

                        condition = abs(stream.samples.shape[0] - SAMPLE_RATE * params['rec_time']) < SAMPLE_NUM_TOLERANCE
                        if condition: results[testName] = "PASSED\n" + stats
                        else: results[testName] = "FAILED\n\tExpected: %d\n\tActual: %d" % (SAMPLE_RATE * params['rec_time'], stream.samples.shape[0]) + "\n" + stats

                        record_count += 1

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

    parser = argparse.ArgumentParser(description='Test Audio Device Configuration')
    parser.add_argument('--fetch', required=False, type=int, default=1)
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../../configs/file_reader_config.xml'))
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=5)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=1)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--engine', required=False, type=str, default='engine=0')

    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)
