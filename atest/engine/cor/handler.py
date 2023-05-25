from __future__ import annotations

import copy
import sys
import re

import time
from abc import ABC, abstractmethod
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from atest.engine.cor.ex.testExecException import TestExecException
from atest.engine.writer.xlsWriter import XlsWriter
from atest.engine.constants import Constants


class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, driver) -> Optional[str]:
        pass


class AbstractHandler(Handler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    def __init__(self, name, sleep, default_sleep, description):
        self.name = name
        # check for override sleep time
        self.sleep = sleep if sleep else default_sleep
        self.description = description
        self.params = []


    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler

    def set_first(self, handler: Handler) -> Handler:
        if handler is not None:
            self._first_handler = handler
        else:
            self._first_handler = self

    def get_next(self):
        if self._next_handler:
            return self._next_handler
        else:
            return None

    def get_input_value(self):
        try:
            if self.input_value:
                return self.input_value
            else:
                return ""
        except Exception as ex:
            return ""

    # return the last handler of the handler chain
    def find_my_last_handler(self) -> AbstractHandler:
        last_hanlder = None
        if self.get_next() is None:
            last_hanlder =  self
        else:
            last_hanlder = self.get_next().find_my_last_handler()
        return last_hanlder

    @abstractmethod
    def handle(self, driver):

        print(f"wait {self.sleep}")
        time.sleep(self.sleep)

        # write test OK in logger file
        xlswriter = XlsWriter()
        xlswriter.write_file(self, Constants.STATUS_OK, None)

        # check if there is another handler, if not
        # this is the last so the test is completed
        if self._next_handler:
            return self._next_handler.handle(driver)
        else:
            print("test finished successfully")

    # common method to get the correct variable
    # to identify items in page
    def get_reference(self, exp_type):
        if exp_type == "CLASS_NAME":
            return By.CLASS_NAME
        elif exp_type == "NAME":
             return By.NAME
        elif exp_type == "XPATH":
             return By.XPATH  


    # recursive method for cloning handler object and
    # his next handlers. This is for the common steps
    # to manage different next handlers
    @staticmethod
    def clone_handler(handler: AbstractHandler, params: dict):
        returnHandler = copy.copy(handler)
        # check if the handler as var params and inject
        # th match in on input values starts by # char
        if re.findall(r"#param[0-9]", returnHandler.get_input_value()):
            for key in params:
                if key == returnHandler.input_value.replace('#',''):
                    returnHandler.input_value = params[key]
        if handler.get_next():
            returnHandler.set_next(AbstractHandler.clone_handler(handler.get_next(), params))
        else:
            return returnHandler

        return returnHandler



'''
Handler per la navigazione verso una url
'''
class GoToHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, link, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.link = link

    # handle: retrive the link and redirect the browse to that link
    def handle(self, driver):

        print(f"GoToHandler handler {self.description}")

        try:
            driver.get(self.link)
        except Exception as ex:
            print(ex)
            raise TestExecException(self, str(sys.exc_info()[1]))

        super().handle(driver)


'''
click handler manages the logic for click action in the page (buttons, href.....)
'''
class ClickHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_type, exp_value, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_type = exp_type
        self.exp_value = exp_value


    def handle(self, driver):

        print(f"click handler {self.description}")

        try:
            # get the correct reference
            button = driver.find_element(super().get_reference(self.exp_type),
                                              self.exp_value)

            #click action
            button.click()
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))

        # next step
        super().handle(driver)

'''
Handler per l'inputazione dati nei campi in maschera
'''
class SetKeysHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_type, exp_value, input_value, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_type = exp_type
        self.exp_value = exp_value
        self.input_value = input_value

    def handle(self, driver):
        print(f"SetKeysHandler handler {self.description}")

        try:
            field = driver.find_element(super().get_reference(self.exp_type),
                                             self.exp_value)
            field.send_keys(self.input_value)
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))

        super().handle(driver)

'''
Handler la cancellazione dei caratteri dai campi di input
'''
class EraseHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_type, exp_value, times, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_type = exp_type
        self.exp_value = exp_value
        self.times = times

    def handle(self, driver):
        print(f"EraseHandler handler {self.description}")

        try:
            field = driver.find_element(super().get_reference(self.exp_type),
                                             self.exp_value)
            for t in range(self.times):
                field.send_keys(Keys.BACK_SPACE)
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))

        super().handle(driver)        

'''
Handler la cancellazione dei caratteri dai campi di input
'''
class CheckConditionHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_type, exp_value, exp_condition, input_value, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_type = exp_type
        self.exp_value = exp_value
        self.exp_condition = exp_condition
        self.input_value = input_value

    def handle(self, driver):
        print(f"CheckConditionHandler handler {self.description}") 

        try:
            # get field value
            u_field = driver.find_element(super().get_reference(self.exp_type),
                                             self.exp_value)
            u_field_value = u_field.get_attribute("value")

            if self.exp_condition == 'eq' and u_field_value != self.input_value:
                raise TestExecException(self, f"{u_field_value} not equal to {self.input_value}")
            elif self.exp_condition == 'gt' and u_field_value < self.input_value:
                raise TestExecException(self, f"{u_field_value} minor than {self.input_value}")
            elif self.exp_condition == 'mt' and u_field_value > self.input_value:
                raise TestExecException(self, f"{u_field_value} greather than {self.input_value}")
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))

        super().handle(driver)        

'''
Handler per il check delle condizioni puntuali
'''
class CheckConditionHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_type, exp_value, exp_condition, input_value, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_type = exp_type
        self.exp_value = exp_value
        self.exp_condition = exp_condition
        self.input_value = input_value

    def handle(self, driver):
        print(f"CheckConditionHandler handler {self.description}") 

        try:
            # get field value
            u_field = driver.find_element(super().get_reference(self.exp_type),
                                             self.exp_value)
            u_field_value = u_field.get_attribute("value")

            if self.exp_condition == 'eq' and u_field_value != self.input_value:
                raise TestExecException(self, f"{u_field_value} not equal to {self.input_value}")
            elif self.exp_condition == 'gt' and u_field_value < self.input_value:
                raise TestExecException(self, f"{u_field_value} minor than {self.input_value}")
            elif self.exp_condition == 'mt' and u_field_value > self.input_value:
                raise TestExecException(self, f"{u_field_value} greather than {self.input_value}")
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))

        super().handle(driver)                

'''
Handler per la gestioni di componenti common
'''
class ManageModuleHandler(AbstractHandler):

    def __init__(self, name, next_handler: Handler, exp_value, modules, sleep, default_sleep, description):
        super().__init__(name, sleep, default_sleep, description)
        self._next_handler: Handler = next_handler
        self.exp_value = exp_value,
        self.modules = modules

    def searchForModule(self):
        for m in self.modules:
            if m == self.modules.exp_value:
                return self.modules
                break  


    def handle(self, driver):
        print(f"ManageModuleHandler handler {self.description}") 

        try:
            self.searchForModule().handle(driver)
        except Exception as ex:
            raise TestExecException(self, str(sys.exc_info()[1]))
        
        super().handle(driver)
  