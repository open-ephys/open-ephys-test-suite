from open_ephys.control import OpenEphysHTTPServer

import time
"""
Test Name: Add/Delete all default plugins
Test Description: Add and delete all default plugins from the signal chain
"""

def test(gui):

    # Store test results to report in a dictionary
    results = {}

    # Add File Reader
    testName = 'Add File reader  to existing chain'
    data = gui.add_processor("File Reader")

    numProcessorsAfterAdd = len(gui.get_processors())

    if numProcessorsAfterAdd == 1:
        results[testName] = "PASSED"
    else:
        results[testName] = "FAILED\n\t" + str(data)
    
    # print(gui.get_processors("File Reader")[0]['id'])

    # Loop through all the plugins in the processor list, add and then remove them one by one
    for plugin in gui.get_processor_list():

        # Skip File Reader, Merger, and Splitter
        if plugin == "File Reader":
            continue

        # Add plugin
        gui.add_processor(plugin)
        numProcessorsAfterAdd = len(gui.get_processors())

        # Check if plugin was added successfully
        if numProcessorsAfterAdd == 2:
            results[f"Add {plugin} to existing chain"] = "PASSED"
        else:
            results[f"Add {plugin} to existing chain"] = f"FAILED\n\t{plugin} was not added successfully"

        processorId = gui.get_processors(plugin)[0]['id']

        # Remove plugin
        gui.delete_processor(processorId)
        numProcessorsAfterRemove = len(gui.get_processors())

        # Check if plugin was removed successfully
        if numProcessorsAfterRemove == 1:
            results[f"Remove {plugin} from existing chain"] = "PASSED"
        else:
            results[f"Remove {plugin} from existing chain"] = f"FAILED\n\t{plugin} was not removed successfully"

    gui.quit()

    return results

'''
================================================================================================================================================
'''


if __name__ == '__main__':

    results = test(OpenEphysHTTPServer())

    for test, result in results.items():
        print(test, '-'*(80-len(test)), result)