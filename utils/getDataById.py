import aiohttp

from termcolor import cprint

from utils.sendErrorMessage import sendErrorMessage   

async def getDataById(url, uuid):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{url}?uuid={uuid}") as result:
                return await result.json()

        except Exception as e:
            cprint(f"[ERROR] in getDataById(): {e}", "red")
            await sendErrorMessage(f"[ERROR] in getDataById(): {e}")
            return