from atest.engine.writer.xlsWriter import XlsWriter
from atest.engine.constants import Constants


class TestExecException(Exception):
    def __init__(self, handler, message) -> None:
        print(f"TestExecException in {handler.description} MESSAGE IS {message}")
        xlswriter = XlsWriter()
        xlswriter.write_file(handler, Constants.STATUS_KO, message)
