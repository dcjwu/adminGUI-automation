import requests

from .logger import Logger, LoggerType
from .utility import Utility


class Notifier:

    def __init__(self, bot_id: str, chat_id: str):
        self.bot_id = bot_id
        self.chat_id = chat_id

    def send(self, text: str):
        url = f'https://api.telegram.org/bot{self.bot_id}/sendMessage?chat_id={self.chat_id}&text={text}'
        res = requests.get(url)

        if res.status_code != 200:
            Logger.log(LoggerType.ERROR, 'Unable to send message to Telegram, please contact Admin.', 'send_message()')
        else:
            Logger.log(LoggerType.DONE, f'Telegram message sent successfully at {Utility.get_str_time()}.')
