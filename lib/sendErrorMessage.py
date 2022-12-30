import aiohttp

from termcolor import cprint

from env import tgToken, tgChat

apiUrl = f'https://api.telegram.org/bot{tgToken}/sendMessage'

async def sendErrorMessage(text):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=f"{apiUrl}", data={"chat_id": tgChat, "text": text}) as response:
                if response.status != 200:
                    cprint(f"[ERROR] in sendErrorMessage: Unable to send message to chat", "red")

        except Exception as e:
            cprint(f"[ERROR] in sendErrorMessage: {e}", "red")
            return