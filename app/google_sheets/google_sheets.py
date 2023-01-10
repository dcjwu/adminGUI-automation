import sys

from googleapiclient.errors import HttpError
from pygsheets import authorize

from app.logger.logger import Logger, LoggerType


class GoogleSheets:
    def __init__(self, key) -> None:
        self.client = authorize()
        self.key = key
        self.sheet = None

    def connect(self):
        try:
            sheet = self.client.open_by_key(self.key).sheet1
            Logger.log(LoggerType.LOG, f"Connected to Google Sheet {self.key}.")
            self.sheet = sheet
        except HttpError:
            Logger.log(LoggerType.ERROR, "Google Sheet not found, please double check the ID.", "connect()")
            sys.exit()
        except Exception as e:
            Logger.log(LoggerType.ERROR, f"Unable to connect to Google Sheet, {e}.", "connect()")
            sys.exit()

    def get_values(self, column):
        values = self.sheet.get_values(column, column)
        unpacked_values = []

        for val in values:
            unpacked_values.append(val[0])

        [is_empty, real_values] = self._count_values(unpacked_values)
        if is_empty:
            Logger.log(LoggerType.ERROR, f"No data found in column {column}.", "get_values()")
            sys.exit()
        else:
            return len(real_values), unpacked_values

    @staticmethod
    def _count_values(values):
        is_empty = False
        not_empty_values = []

        for val in values:
            if val == "":
                is_empty = True
            else:
                is_empty = False
                not_empty_values.append(val)

        return is_empty, not_empty_values

