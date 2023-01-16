import asyncio
import os
import aiohttp
import requests

from app.telegram.telegram import Telegram
from app.logger.logger import Logger, LoggerType
from app.google_sheets.google_sheets import GoogleSheets
from app.admin_panel.admin_panel import AdminPanel

tg = Telegram(os.getenv("TG_TOKEN"), os.getenv("TG_CHAT"))


async def main():
    key = input("Please, enter Google Sheet ID: ")

    gs = GoogleSheets(key)
    gs.connect()

    while True:
        column = input("Please, enter column letter: ").upper()
        if len(column) != 1:
            Logger.log(LoggerType.WARN, "Column should be one character.")
            continue
        if not column.isalpha():
            Logger.log(LoggerType.WARN, "Column can contain only letters.")
            continue
        else:
            break

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
        Logger.log(LoggerType.LOG, f"Handling job {index + 1} of {len(values)}...")
        return_url = await admin.get_return_url(uid)
        await admin.get_redirects(return_url)

    # TODO:

    # try:
    #     async with session.get(f"{adminUrl}?uid=5fe6b7ec-f855-4561-9191-1104bbfb5d5c") as result:
    #         print(await result.text())
    #
    # except Exception as e:
    #     cprint(f"[ERROR] in getDataById(): {e}", "red")
    #     await sendErrorMessage(f"[ERROR] getting data by id: {e}")
    #     sys.exit()

    # print(await getDataById(adminUrl, creds[1]), "SUCCESS")

    # iteration = 0
    # nameValue = None
    # idValue = None

    # for index, id in enumerate(ids):
    #     sleep(1.2)

    #     iteration += 1
    #     cprint(f"[LOG]: Handling job {iteration} of {len(ids)}...", "magenta")

    #     response = await getDataById(adminUrl, id)
    #     result = await unpackList(response, id)

    #     try:
    #         nameValue = result["name"]
    #     except:
    #         nameValue = "Unable to get the name"
    #         cprint(f"[ERROR] in main(): Unable to get the name. TX: {id}", "red")
    #         await sendErrorMessage(f"[ERROR] in main(): Unable to get the name.\n TX: {id}")

    #     try:
    #         idValue = result["id"]
    #     except:
    #         idValue = "Unable to get the ID"
    #         cprint(f"[ERROR] in main(): Unable to get the ID. TX: {id}", "red")
    #         await sendErrorMessage(f"[ERROR] in main(): Unable to get the ID.\n TX: {id}")

    #     try:
    #         sheet.update_values(crange=f"B{index + 2}:C{index + 2}", values=[[nameValue, idValue]])
    #     except Exception as e:
    #         cprint(f"[ERROR] in main(): Unable to set data to Google Sheets: {e}. TX: {id}", "red")
    #         await sendErrorMessage(f"[ERROR] in main(): Unable to set data to Google Sheets: {e}\n TX: {id}")


if __name__ == "__main__":
    asyncio.run(main())
