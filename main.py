import pygsheets
import asyncio

from termcolor import cprint
from time import sleep
from asyncstdlib.builtins import map as amap
from asyncstdlib.builtins import list as alist

from lib.getDataById import getDataById
from lib.unpackList import unpackList
from lib.sendErrorMessage import sendErrorMessage

from env import ssKey

async def main():

    googleSheetsClient = pygsheets.authorize()
    sheet = googleSheetsClient.open_by_key(ssKey).sheet1

    columnA = sheet.get_values("A", "A")
    del columnA[0]

    ids = await alist(amap(unpackList, columnA))

    iteration = 0

    nameValue = None
    idValue = None

    for index, id in enumerate(ids):
        sleep(1.5)

        iteration += 1
        cprint(f"[LOG]: Handling job {iteration} of {len(ids)}...", "magenta")

        response = await getDataById(id)
        result = await unpackList(response, id)

        try:
            nameValue = result["name"]
        except:
            nameValue = "Unable to get the name"
            await sendErrorMessage(f"[ERROR] in main: Unable to get the name. TX ID {id}.")

        try:
            idValue = result["id"]
        except:
            idValue = "Unable to get an ID"
            await sendErrorMessage(f"[ERROR] in main: Unable to get an ID. TX ID {id}.")

        sheet.update_values(crange=f"B{index + 2}:C{index + 2}", values=[[nameValue, idValue]])

if __name__ == "__main__":
    asyncio.run(main())

'''
    1. Add more human readable logs:
        1.1 Public human readable errors to public tg;
        1.2 Dev readable errors to private tg;
    2. Somehow configure script run through UI;
    3. Make choice between apiUrls;
    4. Make user input to add sheet ID;
    5. Write tests and implement CI;
'''