import xlsxwriter
import xlrd
import time
from atest.engine.constants import Constants
from datetime import datetime

class XlsWriter(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(XlsWriter, cls).__new__(cls)
            cls.instance.__cur_row = 0
            cls.instance.__cur_col = 0
            cls.instance.__cur_step = 0
            cls.instance.__name = cls.instance.get_name()
            cls.instance.workbook = xlsxwriter.Workbook(cls.instance.get_name())
            cls.instance.worksheet = cls.instance.workbook.add_worksheet(Constants.WORKBOOK_TAB)
            cls.instance.print_header()
        return cls.instance

    def __init__(self):
        pass

    def get_name(self):
        return Constants.WORKBOOK_NAME + str(time.time()) + '.xlsx'

    def print_header(self):
        # get the workbook
        self.worksheet = self.workbook.get_worksheet_by_name(Constants.WORKBOOK_TAB)
        self.worksheet.write(self.__cur_row,self.__cur_col, 'Test')
        self.increase_col();
        self.worksheet.write(self.__cur_row,self.__cur_col, 'Test Seq')
        self.increase_col();
        self.worksheet.write(self.__cur_row,self.__cur_col, 'Test Name')
        self.increase_col();
        self.worksheet.write(self.__cur_row, self.__cur_col, 'Test Step')
        self.increase_col();
        self.worksheet.write(self.__cur_row, self.__cur_col, 'Test Status')
        self.increase_col();
        self.worksheet.write(self.__cur_row, self.__cur_col, 'Test Time End')
        self.increase_col();
        self.worksheet.write(self.__cur_row, self.__cur_col, 'Test Exception')
        self.reset_col()

        self.increase_row()

    def close_wb(self):
        self.workbook.close()

    def write_file(self, handler, status, message):

        # get current time
        current_time = datetime.now().strftime("%H:%M:%S")

        self.worksheet = self.workbook.get_worksheet_by_name(Constants.WORKBOOK_TAB)
        self.worksheet.write(self.__cur_row,self.__cur_col, self.__parent_name)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, self.instance.__cur_step)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, handler.name)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, handler.description)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, status)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, current_time)
        self.increase_col()
        self.worksheet.write(self.__cur_row,self.__cur_col, message)
        self.reset_col()

        self.increase_row()

        if status == Constants.STATUS_KO or status == Constants.STATUS_NOTRUN:
            if handler.get_next() is not None:
                self.write_file(handler.get_next(), Constants.STATUS_NOTRUN, "")

    def increase_col(self):
        self.__cur_col += 1

    def reset_col(self):
        self.__cur_col = 0

    def increase_row(self):
        self.__cur_row += 1
        self.__cur_step += 1

    def reset_row(self):
        self.__cur_row = 0

    def init_new_test(self, parent_name: str):
        self.__cur_step = 0
        self.__parent_name = parent_name
        self.worksheet = self.workbook.get_worksheet_by_name(Constants.WORKBOOK_TAB)
