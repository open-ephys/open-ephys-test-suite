import platform
import os

def get_recording_dir():
    if platform.system() == 'Windows':
        if os.env("GITHUB_ACTIONS") == "true":
            return 'C:\\open-ephys\\data'
        else:
            os.getenv('OE_RECORD_DIR')
    elif platform.system() == 'Linux':
        return '<path/to/linux/runner>'  # TODO
    else:
        return '<path/to/Mac/runner>'  # TODO