from enum import Enum
from termcolor import cprint


class LoggerType(Enum):
    LOG = "LOG",
    WARN = "WARN",
    ERROR = "ERROR",
    DONE = "DONE"


logger_mapping = {
    LoggerType.LOG: "magenta",
    LoggerType.WARN: "yellow",
    LoggerType.ERROR: "red",
    LoggerType.DONE: "green"
}


class Logger:

    @staticmethod
    def log(logger_type: LoggerType, message, fn_name=None):
        color = logger_mapping.get(logger_type)
        log_str = ""

        if isinstance(logger_type.value, tuple):
            log_str = logger_type.value[0]
        elif isinstance(logger_type.value, str):
            log_str = logger_type.value

        if logger_type == LoggerType.ERROR:
            cprint(f"[{log_str}] in {fn_name}: {message}", color)
        else:
            cprint(f"[{log_str}]: {message}", color)
