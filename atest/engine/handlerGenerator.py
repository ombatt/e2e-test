import copy

from cor.handler import GoToHandler, AbstractHandler, ClickHandler, SetKeysHandler, EraseHandler, CheckConditionHandler, ManageModuleHandler
from abc import ABC, abstractmethod
from selenium import webdriver
from atest.engine.writer.xlsWriter import XlsWriter
import json

class HandlerGenerator:

    def __init__(self) -> None:
        pass

    def chek_for_value(self, item, val):
        try:
            if item[val]:
                return item[val]
        except Exception as ex:
            return None


    def parse_file(self, data, common_modules) -> AbstractHandler:
        # get module name
        name = data['name']    

        # get default sleep
        default_sleep = data['default_sleep']

        driver = None
        # setup the xls writer
        xlswriter = XlsWriter()
        xlswriter.init_new_test(name)

        # declare first handler
        first_handler: AbstractHandler = None

        # declare temp objects
        last_handler: AbstractHandler = None
        cur_handler: AbstractHandler = None

        # loop into test steps
        for i, act in enumerate(data['steps']):

            # initialize the driver for the first handler in the chain
            # all the handlers use the same driver
            # a new driver is created for every test set.

            print(act['action'])

            # initialize correct temp object based on actions
            if act['action'] == "goto":
                cur_handler = GoToHandler(name, None, self.chek_for_value(act, 'link'),
                                        self.chek_for_value(act, 'exp_sleep'),
                                        default_sleep,
                                        self.chek_for_value(act, 'description'))
                
            elif act['action'] == "click":
                cur_handler = ClickHandler(name, None, self.chek_for_value(act, 'exp_type'), 
                                        self.chek_for_value(act, 'exp_value'), 
                                        self.chek_for_value(act, 'exp_sleep'),
                                        default_sleep,
                                        self.chek_for_value(act, 'description'))
                
            elif act['action'] == "send_keys":
                cur_handler = SetKeysHandler(name, None, self.chek_for_value(act, 'exp_type'), 
                                            self.chek_for_value(act, 'exp_value'), 
                                            self.chek_for_value(act, 'input_value'), 
                                            self.chek_for_value(act, 'exp_sleep'),
                                            default_sleep,
                                            self.chek_for_value(act, 'description'))
                
            elif act['action'] == "erase":
                cur_handler = EraseHandler(name, None, self.chek_for_value(act, 'exp_type'), 
                                            self.chek_for_value(act, 'exp_value'), 
                                            self.chek_for_value(act, 'exp_times'), 
                                            self.chek_for_value(act, 'exp_sleep'),
                                            default_sleep,
                                            self.chek_for_value(act, 'description'))

            elif act['action'] == "check_value_condition":
                cur_handler = CheckConditionHandler(name, None, self.chek_for_value(act, 'exp_type'), 
                                            self.chek_for_value(act, 'exp_value'), 
                                            self.chek_for_value(act, 'exp_condition'), 
                                            self.chek_for_value(act, 'input_value'), 
                                            self.chek_for_value(act, 'exp_sleep'),
                                            default_sleep,
                                            self.chek_for_value(act, 'description'))

            # if step module then parse the common module to replace
            # the step with the handler with the name = exp_value
            elif act['action'] == "module":
                for cm in common_modules:
                    if cm.name == self.chek_for_value(act, 'exp_value'):
                        # get the variable params to inject
                        params = self.chek_for_value(act, 'params')
                        cur_handler = AbstractHandler.clone_handler(cm, params)


            # set the next handler in chain or declare the first handler
            if last_handler:
                # find the last handler in the check to set the next
                # that necessary when managing the common type handler
                # who has more next_hanlder
                last_handler.find_my_last_handler().set_next(cur_handler)
            else:
                # first iteration, set the handler as the first
                first_handler = cur_handler

            # set the current handler as last handler
            last_handler = cur_handler
            # override first handler to track the first handler of the chain
            last_handler.set_first(first_handler)

        return first_handler