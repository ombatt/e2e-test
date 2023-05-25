import json
import os
from handlerGenerator import HandlerGenerator
from cor.handler import GoToHandler, AbstractHandler, ClickHandler, SetKeysHandler, EraseHandler, CheckConditionHandler, ManageModuleHandler
from collections.abc import Sequence
import copy
from pathlib import Path
from selenium import webdriver
from atest.engine.writer.xlsWriter import XlsWriter

# path for json steps
path = "./../tests-suites"
files = os.listdir(path)
files = [f for f in files if os.path.isfile(path+'/'+f)]

# module test object list
common_modules = []
# test object list
tests_files = []

handlerGenerator = HandlerGenerator()
xlswriter = XlsWriter()

for fl in files:
    # open test files
    f = open(path+'/'+fl)
    if Path(f.name).suffix != ".json":
        continue

    print(f.name)
    # load into json object
    data = json.load(f)

    # get module type
    module = data['module']
    # if module tipe commong parse the file and put the steps in common_modules
    if module == "common":
        common_modules.append(handlerGenerator.parse_file(data, None))
    else:
        #if not common put the files in test list
        tests_files.append(data)

# parse every single file and execute test immediately
for tf in tests_files:
    try:
        # every test has is own driver
        driver = webdriver.Chrome('./../Lib/chromedriver.exe')
        #get the first handler of the chain
        first_handler = handlerGenerator.parse_file(tf, common_modules)
        # init the test chain
        first_handler.handle(driver)
    except Exception as ex:
        print("exception go to the next test")
        print(ex)
        pass
    finally:
        # quit the test driver
        driver.quit()

xlswriter.close_wb()
