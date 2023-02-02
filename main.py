import os
from asyncio import run

import aiohttp

from app.admin_panel import AdminPanel
from app.browser import Browser
from app.google_sheets import GoogleSheets
from app.logger import Logger, LoggerType
from app.notifier import Notifier
from app.user_input import ColumnType, UserInput
from app.utility import Utility

tg = Notifier(os.getenv('TG_TOKEN'), os.getenv('TG_CHAT'))
user_input = UserInput()
utility = Utility()
logger = Logger()
browser = Browser()


async def main():
    gs_id = user_input.get_default_input('Please, enter Google Sheet ID: ')

    gs = GoogleSheets(gs_id)
    gs.connect()

    input_column = user_input.get_column(ColumnType.INPUT)
    output_column = user_input.get_column(ColumnType.OUTPUT)

    gs.set_output_column(output_column)

    values = gs.get_column_data(input_column)

    admin_url = user_input.get_admin_url()
    admin = AdminPanel(aiohttp.ClientSession(), admin_url)
    await admin.login()

    start_time = utility.get_time()

    for index, tx_id in enumerate(values):
        Logger.log(LoggerType.LOG, f'Handling job {index + 1} of {len(values)}...', None, True)

        return_url = await admin.get_return_url(tx_id)
        redirect_list = await admin.get_redirect_list(return_url)
        gs.write_data(index, redirect_list)

        if index + 1 == len(values):
            end_time = utility.get_time()
            logger.log(LoggerType.DONE, 'Program duration: {}'.format(end_time - start_time) + ' :)', None, True)
            browser.quit()
            await admin.exit()


if __name__ == '__main__':
    run(main())
