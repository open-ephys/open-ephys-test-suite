# Open Ephys Test Suite

Open Ephys Test Suite is a Python library for running automated integration tests with the Open Ephys GUI v1.0+.

The ```tests``` directory contains examples of tests. Tests are organized into two categories:
- **core**: Tests that validate core functionality of the GUI
- **plugins**: Tests that validate functionality of plugins

Before running any test, first launch the GUI with an empty signal chain (Edit->Clear Signal Chain) and ensure the HTTPServer is enabled (File->Enable HTTP Server). You can also run the GUI in headless mode by setting the ```--headless``` flag.

## Single test
To run a single test: 

```python
python tests/core/basic_record.py --fetch 1
```

The **fetch** param is used to determine if new data should be fetched from the GUI during the test:
- Set to **1** if you want to fetch new data from the GUI during the test
- Set to **0** to skip recording new data and use the most recent recorded dataset available in the ```--parent_directory``` parameter.

Additional parameters can be passed to each test, see individual test files for details.

## Run all tests
To run all available tests:

```python
python run_all.py
```