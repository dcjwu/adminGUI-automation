import asyncio
import os
import aiohttp
from datetime import datetime

from app.telegram.telegram import Telegram
from app.logger.logger import Logger, LoggerType
from app.google_sheets.google_sheets import GoogleSheets
from app.admin_panel.admin_panel import AdminPanel

tg = Telegram(os.getenv("TG_TOKEN"), os.getenv("TG_CHAT"))


async def main():
    key = input("Please, enter Google Sheet ID: ")

    gs = GoogleSheets(key)
    gs.connect()

    column = gs.user_input_column_handler("Please, enter INPUT column letter: ")
    gs.get_destination_column()

    program_start_time = datetime.now()

    [count, values] = gs.get_values(column)
    Logger.log(LoggerType.LOG, f"Got {count} values from column {column}.")
    if count != len(values):
        Logger.log(LoggerType.WARN, "It seems like some rows in the column are empty.")
    #
    admin = AdminPanel(aiohttp.ClientSession())
    admin.get_url()

    Logger.log(LoggerType.LOG, "Logging in, please wait...")

    await admin.get_auth_token()
    await admin.login()

    for index, uid in enumerate(values):
        Logger.log(LoggerType.LOG, f"Handling job {index + 1} of {len(values)}...", None, True)
        return_url = await admin.get_return_url(uid)
        redirect_list = await admin.get_redirects(return_url)
        gs.write_to_sheet(index, redirect_list)
        if index+1 == len(values):
            await admin.disconnect()
            program_end_time = datetime.now()
            Logger.log(LoggerType.WARN, "Program duration: {}".format(program_end_time - program_start_time), None, True)


if __name__ == "__main__":
    asyncio.run(main())
