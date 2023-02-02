from enum import Enum

from termcolor import cprint

from .utility import Utility


class LoggerType(Enum):
    LOG = 'LOG',
    WARN = 'WARN',
    ERROR = 'ERROR',
    DONE = 'DONE'


logger_mapping = {
    LoggerType.LOG: 'magenta',
    LoggerType.WARN: 'yellow',
    LoggerType.ERROR: 'red',
    LoggerType.DONE: 'green'
}


class Logger:

    @staticmethod
    def log(logger_type: LoggerType, message: str, fn_name: str = None, is_line_break: bool = False):
        color = logger_mapping.get(logger_type)
        log_str = Utility.enum_to_string(logger_type)

        if logger_type == LoggerType.ERROR:
            if is_line_break:
                cprint(f'\n[{log_str}] in {fn_name}: {message}', color)
            else:
                cprint(f'[{log_str}] in {fn_name}: {message}', color)
        else:
            if is_line_break:
                cprint(f'\n[{log_str}]: {message}', color)
            else:
                cprint(f'[{log_str}]: {message}', color)
