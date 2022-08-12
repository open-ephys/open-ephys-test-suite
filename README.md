# Open Ephys Test Suite

Open Ephys Test Suite is a Python library for performing automated tests with the Open Ephys GUI v0.6.0+.

All tests can be found in the tests directory. The directory includes a template from which all example tests are derived from. Simply copy the template directory and rename it with a meaningful test name. A test requires three files: 

## config.xml

An OpenEphys signal chain configuration to test. The GUI will load this signal chain prior to starting the test. You can build your chain using the GUI and save a copy of it as 'config.xml' in your new test directory.

## config.py

A configuration file that defines paths and parameters to use during the test. 

## test.py  

A test script that uses open-ephys-python-tools to control the GUI and run analysis on any recorded data. 

To run a test called my-test:

1. Launch the GUI and load the config.xml file in my-test directory.
2. Run `python tests/my-test/test.py'