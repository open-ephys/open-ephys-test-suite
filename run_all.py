import os
import platform
import glob 
import pathlib
import time

GUI_EXE = "C:\\Users\\Pavel\\Projects\\Allen\\OpenEphys\\plugin-GUI\\Build\\Release\\open-ephys.exe"

tests = glob.glob(os.path.join(pathlib.Path().absolute(), "tests", "*.py"))

for test in tests:
    print("Running: ", test)
    if platform.system() == 'Windows':
        os.startfile(GUI_EXE)
    rc = os.system("python " + test + " --mode local")
    if rc != 0:
        print("Test failed: ", test)
        break
    time.sleep(4)