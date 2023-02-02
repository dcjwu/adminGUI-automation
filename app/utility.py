from datetime import datetime
from enum import Enum
from time import localtime, strftime


class Utility:

    @staticmethod
    def get_time():
        return datetime.now()

    @staticmethod
    def get_str_time():
        return strftime('%H:%M:%S', localtime())

    @staticmethod
    def enum_to_string(custom_type: Enum):
        str_val = ''
        if isinstance(custom_type.value, tuple):
            str_val = custom_type.value[0]
        elif isinstance(custom_type.value, str):
            str_val = custom_type.value

        return str_val

    @staticmethod
    # -*- coding: utf-8 -*-
    def is_latin_text(text: str):
        try:
            text.encode(encoding='utf-8').decode('ascii')
            return True
        except UnicodeDecodeError:
            return False

    @staticmethod
    def get_letter_with_offset(letter, offset):
        return chr((ord(letter.upper()) + offset - 65) % 26 + 65)
