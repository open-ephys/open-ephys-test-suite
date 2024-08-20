from open_ephys.control import OpenEphysHTTPServer

parameters = {

    'File Reader':      {
                        'selected_file': 'C:\\open-ephys\\data\\test_data.dat',
                        'active_stream' : 0,
                        'start_time' : 0,
                        'end_time' : 0
                        },
    'Bandpass Filter':  {
                        'low_cut': 0,
                        'high_cut': 0,
                        'channels': 0,
                        'threads': 0
                        },
    'Phase Detector':   {
                        'channel' : 0,
                        'ttl_out' : 0,
                        'gate_line' : 0,
                        'phase' : 0
                        },
    'Common Avg Ref':   {
                        'affected' : 0,
                        'reference' : 0,
                        'gain' : 0
                        },
    'Arduino Output':   { 
                        'device' : 0,
                        'output_pin' : 0,
                        'input_pin' : 0,
                        'gate_line' : 0},
    'Audio Monitor':    {
                        'mute_audio' : 0,
                        'audio_output' : 0,
                        'channels' : 0,
                        'spike_channels' : 0
                        },
    'Record Node':      {
                        'directory' : 'Volumes/T7/test-suite',
                        'engine' : 0,
                        'events' : 0,
                        'spikes' : 0,
                        'channels' : 0,
                        'sync_line' : 0,
                        'main_sync' : 0
                        }

}

def test(gui, params):

    results = {}

    for processor in gui.get_processor_list():
        print(processor)
        if processor in parameters:
            gui.clear_signal_chain()
            gui.add_processor("File Reader")
            if processor != "File Reader": gui.add_processor(processor)
            node = gui.get_processors(processor)[0]
            for key in node:
                if key == 'parameters':
                    processor_params = node[key]
                    print(' --PROCESSOR SCOPED' + '-'*50)
                    [print(param) for param in processor_params]
            stream_params = gui.get_parameters(node['id'],0)
            print(" --STREAM SCOPED" + '-'*50)
            [print(param) for param in stream_params['parameters']]

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
    RECORD_PATH = 'C:\\open-ephys\\data'
elif platform.system() == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    RECORD_PATH = '<path/to/mac/runner>' #TODO

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--cfg_path', required=False, type=str, default=os.path.join(Path(__file__).resolve().parent, '../configs/file_reader_config.xml'))
    parser.add_argument('--parent_directory', required=False, type=str, default='C:\\open-ephys\\data')
    params = vars(parser.parse_args(sys.argv[1:]))

    results = test(OpenEphysHTTPServer(), params)

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)