import os
import platform
import glob 
import pathlib
import time

tests = glob.glob(os.path.join(pathlib.Path().absolute(), "tests", "*.py"))

for test in tests:
    print("Running: ", test)
    rc = os.system("python " + test + " --mode local --fetch 1")
    if rc != 0:
        print("Test failed: ", test)
        break
    time.sleep(4)