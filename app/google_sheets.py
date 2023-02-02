import sys

from googleapiclient.errors import HttpError
from pygsheets import authorize

from .logger import Logger, LoggerType
from .utility import Utility


class GoogleSheets:

    def __init__(self, gs_id):
        self.client = authorize()
        self.gs_id = gs_id
        self.sheet = None
        self.output_column = None

    def connect(self):
        try:
            self.sheet = self.client.open_by_key(self.gs_id).sheet1
            Logger.log(LoggerType.DONE, f'Connected to {self.gs_id}.')

        except HttpError as e:
            if e.status_code == 404:
                Logger.log(LoggerType.ERROR, f'Google Sheet with such ID not found.', 'connect()')
            else:
                Logger.log(LoggerType.ERROR, f'Unable to connect to Google Sheet, {e}.', 'connect()')
            sys.exit()
        except Exception as e:
            Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', 'connect()')
            sys.exit()

    def get_column_data(self, column: str):
        raw_values = self.sheet.get_values(column, column)
        del raw_values[0]
        values = []
        for rv in raw_values:
            values.append(rv[0])

        [is_empty, not_empty_count] = self._validate_column_values(values)
        if is_empty:
            Logger.log(LoggerType.ERROR, f'Column {column} is empty.', 'get_column_data()')
            sys.exit()
        else:
            if not_empty_count != len(values):
                Logger.log(LoggerType.WARN, f'Seems like some rows in range are empty.')
            Logger.log(LoggerType.LOG, f'Got {not_empty_count} available values from column {column}.')
            return values

    def write_data(self, index: int, url_list: list):
        if isinstance(url_list, list):
            try:
                end_column = Utility.get_letter_with_offset(self.output_column, len(url_list) - 1)
                self.sheet.update_values(
                    f'{self.output_column}{index + 2}:{end_column}{index + 2}',
                    [url_list]
                )
            except Exception as e:
                Logger.log(
                    LoggerType.ERROR,
                    f'Unable to update column {self.output_column} on row {index + 2}, {e}.',
                    'write_to_sheet()'
                )

    def set_output_column(self, column):
        self.output_column = column

    @staticmethod
    def _validate_column_values(values: list):
        is_empty = True
        not_empty_values = []

        for v in values:
            if v == '':
                is_empty = True
            else:
                is_empty = False
                not_empty_values.append(v)

        return is_empty, len(not_empty_values)
