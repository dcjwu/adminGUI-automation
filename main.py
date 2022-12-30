import os
import sys
import pygsheets
import asyncio
import inquirer

from termcolor import cprint
from time import sleep

from asyncstdlib.builtins import map as amap
from asyncstdlib.builtins import list as alist

from utils.unpackList import unpackList
from utils.getDataById import getDataById
from utils.sendErrorMessage import sendErrorMessage

async def main():
    googleSheetsClient = pygsheets.authorize()

    ssKey = input("Please, add Google Sheet ID: ")
    
    try:
        sheet = googleSheetsClient.open_by_key(ssKey).sheet1
        cprint(f"[LOG]: Connected to Google Sheet {ssKey}", "magenta")
    except Exception as e:
        cprint(f"[ERROR] in main(): Unable to connect to Google Sheet: {e}", "red")
        sys.exit()

    columnA = sheet.get_values("A", "A")
    del columnA[0]

    ids = await alist(amap(unpackList, columnA))
    cprint(f"[LOG]: Got {len(ids)} values from column A", "magenta")

    options = [os.getenv("URL_1"), os.getenv("URL_2")]
    questions = [
        inquirer.List("url",
        message="Please, choose admin URL",
        choices=options)
    ]
    answers = inquirer.prompt(questions)
    adminUrl = answers["url"]
    
    iteration = 0
    nameValue = None
    idValue = None

    for index, id in enumerate(ids):
        sleep(1.2)

        iteration += 1
        cprint(f"[LOG]: Handling job {iteration} of {len(ids)}...", "magenta")

        response = await getDataById(adminUrl, id)
        result = await unpackList(response, id)

        try:
            nameValue = result["name"]
        except:
            nameValue = "Unable to get the name"
            cprint(f"[ERROR] in main(): Unable to get the name. TX: {id}", "red")
            await sendErrorMessage(f"[ERROR] in main(): Unable to get the name.\n TX: {id}")

        try:
            idValue = result["id"]
        except:
            idValue = "Unable to get the ID"
            cprint(f"[ERROR] in main(): Unable to get the ID. TX: {id}", "red")
            await sendErrorMessage(f"[ERROR] in main(): Unable to get the ID.\n TX: {id}")

        try:
            sheet.update_values(crange=f"B{index + 2}:C{index + 2}", values=[[nameValue, idValue]])
        except Exception as e:
            cprint(f"[ERROR] in main(): Unable to set data to Google Sheets: {e}. TX: {id}", "red")
            await sendErrorMessage(f"[ERROR] in main(): Unable to set data to Google Sheets: {e}\n TX: {id}")

if __name__ == "__main__":
    asyncio.run(main())