import time

import requests

from app.logger.logger import Logger, LoggerType


class Telegram:

    def __init__(self, bot_id, chat_id) -> None:
        self.bot_id = bot_id
        self.chat_id = chat_id

    async def send_message(self, text):
        current_time = time.strftime("%H:%M:%S", time.localtime())

        url = f"https://api.telegram.org/bot{self.bot_id}/sendMessage?chat_id={self.chat_id}&text={text}"

        res = requests.get(url)

        if res.status_code != 200:
            Logger.log(LoggerType.ERROR, "Unable to send message to Telegram, please contact Admin.", "send_message()")
        else:
            Logger.log(LoggerType.LOG, f"Telegram message sent successfully at {current_time}.")
