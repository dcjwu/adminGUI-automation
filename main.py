import os
import sys
import pygsheets
import asyncio
import inquirer
import aiohttp

from termcolor import cprint
from time import sleep
from bs4 import BeautifulSoup

from asyncstdlib.builtins import map as amap
from asyncstdlib.builtins import list as alist

from utils.unpackList import unpackList
from utils.sendErrorMessage import sendErrorMessage
from utils.multipartify import multipartify

from admin.isAuth import isAuth

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
    cprint(f"[LOG]: SUCCESS, Got {len(ids)} values from column A", "magenta")

    url1 = os.getenv("URL_1")
    url2 = os.getenv("URL_2")
    options = [url1, url2]
    questions = [
        inquirer.List("url",
        message="Please, choose admin URL",
        choices=options)
    ]
    answers = inquirer.prompt(questions)
    adminUrl = answers["url"]

    authUrl = None

    if adminUrl == os.getenv("URL_1"):
        authUrl = os.getenv("AUTH_1")
    elif adminUrl == os.getenv("URL_2"):
        authUrl = os.getenv("AUTH_2")
    else:
        raise Exception("ERROR, please try again or contact Admin.")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(authUrl) as result:
                html = await result.text()
                soup = BeautifulSoup(html, 'html.parser')
                token = soup.find("input", {"name": "authenticity_token"}).get("value")

        except Exception as e:
            cprint(f"[ERROR] getting auth token(), please contact Admin: {e}", "red")
            return

        try:
            user = None
            password = None

            if adminUrl == os.getenv("URL_1"):
                user = os.getenv("USERNAME_1")
                password = os.getenv("PASS_1")

            elif adminUrl == os.getenv("URL_2"):
                user = os.getenv("USERNAME_2")
                password = os.getenv("PASS_2")

            payload = {
                "authenticity_token": token,
                "user": {
                    "email": user,
                    "password": password,
                    "otp_attempt": ""
                },
                "password": {
                    "visibility": "0"
                },
                "Commit": "Sign In"
            }

            async with session.post(authUrl, data=multipartify(payload)) as result:
                html = await result.text()
                authorized = isAuth(html)

                if (authorized):
                    cprint(f"[LOG] SUCESS, Authorized to admin panel", "magenta")
                else:
                    cprint(f"[ERROR] in attemptLogin(), Unable to authorize to admin panel. Please, contact Admin", "red")
                    sys.exit()

        except Exception as e:
            cprint(f"[ERROR] in login flow: Seems like wrong credentials: {e}", "red")

        try:
            async with session.get(f"{adminUrl}?uid=5fe6b7ec-f855-4561-9191-1104bbfb5d5c") as result:
                print(await result.text())

        except Exception as e:
            cprint(f"[ERROR] in getDataById(): {e}", "red")
            await sendErrorMessage(f"[ERROR] getting data by id: {e}")
            sys.exit()

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

'''
    1. CI to generate requirements;
    2. Dockerize;
    3. Tests?
'''