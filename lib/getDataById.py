import aiohttp

from termcolor import cprint

from lib.sendErrorMessage import sendErrorMessage

from env import apiUrl      

async def getDataById(uuid):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{apiUrl}?uuid={uuid}") as result:
                return await result.json()

        except Exception as e:
            cprint(f"[ERROR] in getDataById: {e}", "red")
            await sendErrorMessage(f"[ERROR] in getDataById: {e}")
            return