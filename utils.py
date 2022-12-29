import aiohttp

from termcolor import cprint

from env import apiUrl      

async def getDataById(uuid):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{apiUrl}?uuid={uuid}") as result:
                return await result.json()

        except Exception as e:
            cprint(f"[ERROR] getDataById: {e}", "red")
            return

def unpackList(item):
    try:
        return item[0]
    except Exception as e:
        cprint(f"[ERROR] unpackList: {e}", "red")
        return