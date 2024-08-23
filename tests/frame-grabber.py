import os
import time
import glob

import numpy as np
import cv2

import pandas as pd
pd.set_option('display.max_rows', None)

from open_ephys.control import OpenEphysHTTPServer
from open_ephys.analysis import Session

import matplotlib.pyplot as plt

import pytesseract
from PIL import Image

from scipy.interpolate import interp1d

class VideoFrame():

    def __init__(self, image_path, sample_number, software_time, clock_time=None):
        self.image_path = image_path
        self.sample_number = sample_number
        self.software_time = software_time
        if clock_time is not None:
            self.clock_time = clock_time
        else:
            self.clock_time = self.extract_time()

    @staticmethod
    def convert_time_to_ms(time_str):
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds, hundredths = map(int, parts[1].split('.'))
        ms_time = (minutes * 60000) + (seconds * 1000) + (hundredths * 10)
        return ms_time

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

        print(f'Detected text: {text}', end=' -> ')

        #fix OCR errors
        text = text.replace('00:24 6 re}','00:24.63')
        text = text.replace('00:27 faye}','00:27.63')
        text = text.replace('00:27. Qa','00:27.94')
        text = text.replace('00:34.9 fe','00:34.93')
        text = text.replace('00:38. nye)','00:38.16')
        text = text.replace('OO: 53.5. 4', '00:53.54')

        text = text.replace(" ", "")
        text = text.replace('OO','00')
        text = text.replace('0G','10')
        text = text.replace('g','8')
        text = text.replace('e','8')
        text = text.replace('B','8')
        text = text.replace('@','4')
        text = text.replace(',','')
        text = text.replace('a','8')
        text = text.replace('%','5')
        text = text.replace('Z','7')
        text = text.replace('z','7')
        text = text.replace('8y8','00')
        text = text.replace('on','07')

        if text == '': text = '00:07.52' #special case?

        if text.count(":") > 1: text = text[::-1].replace(":", ".", 1)[::-1]
        if text.count('.') > 1: text = text.replace(".", ":", 1)
        if '\u00A2' in text: text = text.replace('\u00A2', '7')
        if '.' in text and ':' in text:
            print(f'{text}')
            return self.convert_time_to_ms(text)
        else:
            if '.' not in text:
                #add it to position -2
                text = text[:-3] + '.' + text[-3:]
                print(f'{text}')
                return self.convert_time_to_ms(text)
            else:
                print(f'\t\t {text} is not a valid time')
                return "00:00.00"

class VideoRecording():

    def __init__(self, directory):
        self.directory = directory

        if os.path.exists(os.path.join(self.directory, 'extracted_key_times.txt')):
            with open(os.path.join(self.directory, 'extracted_key_times.txt'), 'r') as f:
                self.key_frame_times = list(map(int, f.readlines()))

        if os.path.exists(os.path.join(self.directory, 'extracted_frame_times.txt')):
            with open(os.path.join(self.directory, 'extracted_frame_times.txt'), 'r') as f:
                self.extracted_frame_times = list(map(int, f.readlines()))

        # find any duplicates in extracted_frame_times
        seen = set()
        duplicates = set()
        for time in self.extracted_frame_times:
            if time in seen:
                duplicates.add(time)
            else:
                seen.add(time)
        print(f"Found {len(duplicates)} duplicates in extracted_frame_times")

        self.key_frames = []
        self.extracted_frames = []
        self._load_key_frames()
        self._load_images()
        self._process_images()

        #load line from sync_messages.txt
        sync_messages = []
        if os.path.exists(os.path.join(self.directory, 'sync_messages.txt')):
            with open(os.path.join(self.directory, 'sync_messages.txt'), 'r') as f:
                sync_messages = f.readlines()
        first_recorded_software_time = sync_messages[0].split()[-1]

        for frame in self.extracted_frames:
            #find exact match in key_frames
            for key_frame in self.key_frames:
                if key_frame.clock_time == frame.clock_time:
                    print(f"Matched {key_frame.clock_time} with {frame.clock_time}")
                
        


    def _load_key_frames(self):
        timestamps_file = os.path.join(self.directory, 'frame_timestamps.csv')
        self.timestamps = np.loadtxt(timestamps_file, delimiter=',')

        for i, row in enumerate(self.timestamps):
            img_path = os.path.join(self.directory, 'frames', f"frame at {int(row[0]):010d}.jpg")
            sample_number = int(row[3])
            software_time = row[4]
            if self.key_frame_times is not None:
                self.key_frames.append(VideoFrame(img_path, int(sample_number), software_time, self.key_frame_times[i]))
            else:
                self.key_frames.append(VideoFrame(img_path, int(sample_number), software_time))

        if not self.key_frame_times:
            frame_times = [key_frame.time for key_frame in self.key_frames]
            with open(os.path.join(self.directory, 'extracted_key_times.txt'), 'w') as f:
                f.write('\n'.join(map(str, frame_times)))

            self.key_frame_times = frame_times

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
            print(f"Found {len(images)} frames")

        self.images = images

    def _process_images(self):

        if self.extracted_frame_times is None:
            for image in self.images:
                img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
                #intensities.append(np.sum(img))
                self.extracted_frames.append(VideoFrame(image, -1, -1))
            frame_times = [key_frame.time for key_frame in self.key_frames]
            with open(os.path.join(self.directory, 'extracted_frame_times.txt'), 'w') as f:
                f.write('\n'.join(map(str, frame_times)))

            self.extracted_frame_times = frame_times

        else: 

            for i, image in enumerate(self.images):
                #img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
                #intensities.append(np.sum(img))
                self.extracted_frames.append(VideoFrame(image, -1, -1, self.extracted_frame_times[i]))

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
            
            for directory in recording_directories:
            
                recordings.append(VideoRecording(directory))
                
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

    node = session.recordnodes[0]

    recording = node.recordings[0]

    duration_sec = len(recording.continuous[0].samples) / recording.continuous[0].metadata['sample_rate']

    results["Recording duration"] = duration_sec

    events_by_sample_number = recording.events.sort_values(by='sample_number')

    received_events = events_by_sample_number[events_by_sample_number["stream_name"] == "Probe-A-AP"]

    results["Key frame events"] = len(received_events["sample_number"])

    frame_grabber_nodes = detect_frame_grabbers(path)

    video = frame_grabber_nodes[0].recordings[0]

    results["Extracted frames"] = len(video.images)
    results["fps"] = int(len(video.images) / duration_sec)

    SHOW = False
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
    parser.add_argument('--mode', required=False, choices={'local', 'githubactions'})
    parser.add_argument('--fetch', required=False, type=int, default=1)
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