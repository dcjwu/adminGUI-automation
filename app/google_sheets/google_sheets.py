import sys

from pygsheets import authorize

from app.logger.logger import Logger, LoggerType


class GoogleSheets:
    def __init__(self, key) -> None:
        self.client = authorize()
        self.key = key
        self.sheet = None
        self.output_column = None

    def connect(self):
        try:
            sheet = self.client.open_by_key(self.key).sheet1
            Logger.log(LoggerType.LOG, f"Connected to Google Sheet {self.key}.")
            self.sheet = sheet

        except Exception as e:
            Logger.log(LoggerType.ERROR, f"Unable to connect to Google Sheet, {e}.", "connect()")
            sys.exit()

    def get_destination_column(self):
        column = self.user_input_column_handler("Please enter OUTPUT column letter: ")
        self.output_column = column

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
            del unpacked_values[0]
            return (len(real_values) - 1), unpacked_values

    def write_to_sheet(self, index, url_list):
        if isinstance(url_list, list):
            try:
                final_column = self._get_letter(self.output_column, len(url_list) - 1)
                self.sheet.update_values(
                    f"{self.output_column}{index + 2}:{final_column}{index + 2}",
                    [url_list]
                )
            except Exception as e:
                Logger.log(
                    LoggerType.ERROR,
                    f"Unable to update column {self.output_column} on row {index + 2}, {e}.",
                    "write_to_sheet()"
                )

    @staticmethod
    def user_input_column_handler(message):
        while True:
            column = input(message).upper()
            if len(column) != 1:
                Logger.log(LoggerType.WARN, "Column should be one character.")
                continue
            if not column.isalpha():
                Logger.log(LoggerType.WARN, "Column can contain only letters.")
                continue
            else:
                return column

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

    @staticmethod
    def _get_letter(letter, offset):
        return chr((ord(letter.upper()) + offset - 65) % 26 + 65)
