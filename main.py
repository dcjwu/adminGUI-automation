import pygsheets
import asyncio

from termcolor import cprint
from time import sleep

from utils import getDataById
from utils import unpackList

from env import ssKey

googleSheetsClient = pygsheets.authorize()
sheet = googleSheetsClient.open_by_key(ssKey).sheet1

columnA = sheet.get_values("A", "A")
del columnA[0]

ids = list(map(unpackList, columnA))

async def main():

    iteration = 0

    nameValue = None
    idValue = None

    for index, id in enumerate(ids):
        sleep(1.5)

        iteration += 1
        cprint(f"[LOG]: Handling job {iteration} of {len(ids)}...", "magenta")

        response = await getDataById(id)
        result = unpackList(response)

        try:
            nameValue = result["name"]
        except:
            nameValue = "Unable to get the name"

        try:
            idValue = result["id"]
        except:
            idValue = "Unable to get an ID"

        sheet.update_values(crange=f"B{index + 2}:C{index + 2}", values=[[nameValue, idValue]])

asyncio.run(main())

'''
    1. Add more human readable logs;
    2. Somehow configure script run through UI;
    3. Make choice between apiUrls;
    4. Make user input to add sheet ID;
'''