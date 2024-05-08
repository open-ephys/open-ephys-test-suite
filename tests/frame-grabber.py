import os
import time
import glob

import numpy as np
import cv2

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

#disable data frame preview limit
import pandas as pd
pd.set_option('display.max_rows', None)

import pytesseract
from PIL import Image

def convert_time_to_ms(time_str):
    parts = time_str.split(':')
    minutes = int(parts[0])
    seconds, hundredths = map(int, parts[1].split('.'))
    return (minutes * 60000) + (seconds * 1000) + (hundredths * 10)

class KeyFrame():

    def __init__(self, image_path, sample_number, software_time):
        self.image_path = image_path
        self.sample_number = sample_number
        self.software_time = software_time
        self.time = self.extract_time()

    def extract_time(self):
        image = cv2.imread(self.image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        #hard-coded cropping centered on time
        x_start = 4 * w // 9
        x_end = 8 * w // 13
        y_start = h // 4
        y_end = h // 3
        
        cropped = gray[y_start:y_end, x_start:x_end]
        resized = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        clean = cv2.medianBlur(resized, 3)

        pil_image = Image.fromarray(clean)
        text = pytesseract.image_to_string(pil_image)

        return convert_time_to_ms(text.replace(" ", ""))

class VideoRecording():

    def __init__(self, directory, experiment_index, recording_index):
        self.directory = directory
        self.experiment_index = experiment_index
        self.recording_index = recording_index

        self._load_timestamps()
        EXTRACT_FRAMES = False
        if EXTRACT_FRAMES:
            self._load_images()
            self._process_images()
        #self._show()

    def _load_timestamps(self):
        timestamps_file = os.path.join(self.directory, 'frame_timestamps.csv')
        self.timestamps = np.loadtxt(timestamps_file, delimiter=',')
        self.sample_numbers = self.timestamps[:, 3]

    def _load_images(self):
        images = []
        cap = cv2.VideoCapture(os.path.join(self.directory, 'video.mov'))
        frames_dir = os.path.join(self.directory, 'extracted_frames')

        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir, exist_ok=True)
            frame_num = 0
            while True:
                success, frame = cap.read()
                if not success:
                    break
                frame_file = os.path.join(frames_dir, f"frame_{frame_num:04d}.jpg")
                images.append(frame_file)
                cv2.imwrite(frame_file, frame)
                frame_num += 1

            # Release the video capture object
            cap.release()
        else:
            print(f"Directory {frames_dir} already exists...loading frames from disk...")
            for frame_file in glob.glob(os.path.join(frames_dir, '*.jpg')):
                images.append(frame_file)

        self.images = images

    def _process_images(self):
        
        intensities = []

        for image in self.images:
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            intensities.append(np.sum(img))

        values = intensities
        peaks = []
        troughs = []
        for i in range(1, len(values) - 1):
            # Detect peaks
            if values[i-1] < values[i] > values[i+1]:
                # Ensure the last detected point was not a peak to avoid consecutive peaks
                if not peaks or (peaks and peaks[-1][0] != i-1):
                    peaks.append((i, values[i]))
            # Detect troughs
            elif values[i-1] > values[i] < values[i+1]:
                # Ensure the last detected point was not a trough to avoid consecutive troughs
                if not troughs or (troughs and troughs[-1][0] != i-1):
                    troughs.append((i, values[i]))

        self.intensities = intensities
        self.peaks = peaks
        self.troughs = troughs

    def _show(self):
        import matplotlib.pyplot as plt
        
        plt.plot(self.intensities, 'b-')
        plt.scatter(*zip(*self.peaks), color='green')
        plt.scatter(*zip(*self.troughs), color='red')

        ANNOTATE = True
        if ANNOTATE:
            for i, txt in enumerate(self.peaks):
                plt.annotate(txt[0], (self.peaks[i][0], self.peaks[i][1]))
            for i, txt in enumerate(self.troughs):
                plt.annotate(txt[0], (self.troughs[i][0], self.troughs[i][1]))

        plt.gcf().set_size_inches(30, 13.5)
        plt.show()

class FrameGrabber():

    def __init__(self, directory):
        
        self.directory = directory
        
        self._detect_recordings()

    def _detect_recordings(self):
        
        recordings = []
        
        experiment_directories = glob.glob(os.path.join(self.directory, 'experiment*'))
        experiment_directories.sort()

        for experiment_index, experiment_directory in enumerate(experiment_directories):
             
            recording_directories = glob.glob(os.path.join(experiment_directory, 'recording*'))
            recording_directories.sort()
            
            for recording_index, recording_directory in enumerate(recording_directories):
            
                recordings.append(VideoRecording(recording_directory, 
                                                       experiment_index,
                                                       recording_index))
                
        self.recordings = recordings

def detect_frame_grabbers(directory):
    framegrabberpaths = glob.glob(os.path.join(directory, 'Frame Grabber *'))
    framegrabberpaths.sort()
    return [FrameGrabber(path) for path in framegrabberpaths]

"""
Test Name: FrameGrabber Test
Test Description: Test FrameGrabber plugin
"""
def test(gui, params):

    results = {}

    # Fetch fesh data if needed
    if params['fetch']:

        # Load config for this test
        if params['mode'] == 'local':
            gui.load(params['cfg_path'])
            time.sleep(2)

        # Set record path for RecordNode 
        for node in gui.get_processors("Record Node"):
            print(f"Setting record path to {params['parent_directory']}.")
            #gui.set_record_engine(node['id'], params['engine'])
            gui.set_processor_parameter(node['id'], 'engine', params['engine'])
            #gui.set_record_path(node['id'], params['parent_directory'])
            gui.set_processor_parameter(node['id'], 'directory', params['parent_directory'])

        for node in gui.get_processors("Frame Grabber"):
            gui.set_processor_parameter(node['id'], 'directory_name', params['parent_directory'])

        # Acquire and record data
        for _ in range(params['num_exp']):

            for _ in range(params['num_rec']):

                gui.acquire()
                time.sleep(params['acq_time'])
                gui.record()
                time.sleep(params['rec_time'])

            gui.idle()

    path = gui.get_latest_recordings(params['parent_directory'], 1)[0]

    session = Session(path)

    print(path)

    node = session.recordnodes[0]

    recording = node.recordings[0]

    duration_sec = len(recording.continuous[0].samples) / recording.continuous[0].metadata['sample_rate']

    results["Recording duration"] = duration_sec

    events_by_sample_number = recording.events.sort_values(by='sample_number')

    #sent_events = events_by_sample_number[events_by_sample_number["stream_name"] == "Source_Sim-1100"]

    received_events = events_by_sample_number[events_by_sample_number["stream_name"] == "PXIe-6341"]

    results["Received events"] = len(received_events["sample_number"])

    frame_grabber_nodes = detect_frame_grabbers(path)

    video = frame_grabber_nodes[0].recordings[0]

    results["Extracted frames"] = len(video.images)

    SHOW = True
    if SHOW:
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, 1, figsize=(30, 12), sharex=True)
        axs[0].plot(received_events['sample_number'][:-1], np.diff(received_events['sample_number']))

        #iterate over rows with iterrows()
        for i, row in received_events.iterrows():
            axs[0].axvline(x=row['sample_number'], color='green' if row['state'] == 1 else 'red', alpha=0.5)

        ANNOTATE = False
        if ANNOTATE:
            for i, txt in enumerate(received_events['sample_number']):
                axs[0].annotate(txt[0], (video.peaks[i][0], video.peaks[i][1]))

        PLOT_AS_SCATTER: bool = False
        if PLOT_AS_SCATTER:
            axs[1].scatter(*zip(*video.peaks), color='green')
            axs[1].scatter(*zip(*video.troughs), color='red')
        else:
            #plot as vertical lines
            for peak in video.peaks:
                axs[1].axvline(x=video.sample_numbers[peak[0]], color='green')
            for trough in video.troughs:
                axs[1].axvline(x=video.sample_numbers[trough[0]], color='red')

        plt.show()
        #print(video.sample_numbers)

    TEST_FRAME_COUNT = False
    if TEST_FRAME_COUNT:
        testName = 'timestamps count == frame count'
        video = frame_grabber_nodes[0].recordings[0]
        if len(video.timestamps) == len(video.images):
            results[testName] = "PASSED"
        else:
            results[testName] = "FAILED\n\tFound %d timestamps and %d images" % (len(video.timestamps), len(video.images))

    return results

'''
================================================================================================================================================
'''
import sys
import argparse
import platform

from pathlib import Path

if platform.system() == 'Windows':
    RECORD_PATH = 'D:\\test-suite'
elif platform.system() == 'Linux':
    RECORD_PATH = '<path/to/linux/runner>' #TODO
else:
    RECORD_PATH = '/Volumes/T7/test-suite'

CONFIG_FILE = os.path.join(Path(__file__).resolve().parent, '../configs/frame-grabber/frame-grabber.xml')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mode', required=True, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=True, type=int, default=1)
    parser.add_argument('--address', required=False, type=str, default='http://127.0.0.1')
    parser.add_argument('--cfg_path', required=False, type=str, default=CONFIG_FILE)
    parser.add_argument('--acq_time', required=False, type=int, default=2)
    parser.add_argument('--rec_time', required=False, type=int, default=10)
    parser.add_argument('--num_rec', required=False, type=int, default=1)
    parser.add_argument('--num_exp', required=False, type=int, default=1)
    parser.add_argument('--prepend_text', required=False, type=str, default='')
    parser.add_argument('--base_text', required=False, type=str, default='')
    parser.add_argument('--append_text', required=False, type=str, default='')
    parser.add_argument('--parent_directory', required=False, type=str, default=RECORD_PATH)
    parser.add_argument('--engine', required=False, type=str, default='0') #"engine=1" vs. just 1

    params = vars(parser.parse_args(sys.argv[1:]))

    start_time = time.time()

    results = test(OpenEphysHTTPServer(), params)

    print(f"Test took {time.time() - start_time} seconds")

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)