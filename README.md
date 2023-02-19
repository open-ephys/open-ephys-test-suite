# Open Ephys Test Suite

Open Ephys Test Suite is a Python library for performing automated tests with the Open Ephys GUI v0.6.0+.

The ```tests``` directory contains examples of tests.

Before running any test, first launch the GUI with an empty signal chain (Edit->Clear Signal Chain) and ensure the HTTPServer is enabled (File->Enable HTTP Server). 

## Single test
To run a single test: 

```python
python tests/basic_record.py --mode local --fetch 1
```

The **mode** param is required for all calls:
- Set to **local** if running on your own machine
- Set to **githubactions** if running on a Github Actions runner

The **fetch** param is required for any tests that involve recordings:
- Set to **1** if you want to fetch new data from the GUI during the test
- Set to **0** to skip recording new data and use an existing dataset.

Additional parameters can be passed to each test, see individual test files for details.

## All tests
To run all available tests:

```python
python run_all.py
```
