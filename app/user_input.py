from enum import Enum

import inquirer

from .admin_panel import admin_mapping
from .logger import Logger, LoggerType
from .utility import Utility


class ColumnType(Enum):
    INPUT = 'INPUT',
    OUTPUT = 'OUTPUT'


class UserInput:

    @staticmethod
    def get_default_input(text: str):
        return input(text)

    @staticmethod
    def get_column(column_type: ColumnType):
        col_str = Utility.enum_to_string(column_type)

        while True:
            column = input(f'Please, enter {col_str} column: ').upper()
            if len(column) != 1:
                Logger.log(LoggerType.WARN, 'Column should be one (1) character.')
                continue
            if not column.isalpha():
                Logger.log(LoggerType.WARN, 'Column can contain only letters.')
                continue
            if not Utility.is_latin_text(column):
                Logger.log(LoggerType.WARN, 'Please, use latin characters.')
                continue
            else:
                return column

    @staticmethod
    def get_admin_url():
        attributes = [
            inquirer.List(
                'admin_url',
                message='Please, choose Admin Panel URL',
                choices=list(admin_mapping.keys())
            )
        ]
        user_input = inquirer.prompt(attributes)
        return user_input['admin_url']
