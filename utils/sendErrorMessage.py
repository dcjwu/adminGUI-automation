import os
import aiohttp

from termcolor import cprint

tgUrl = f'https://api.telegram.org/bot{os.getenv("TG_TOKEN")}/sendMessage'

async def sendErrorMessage(text):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=f"{tgUrl}", data={"chat_id": os.getenv("TG_CHAT"), "text": text}) as response:
                if response.status != 200:
                    cprint(f"[ERROR] in sendErrorMessage(): Unable to send message to chat, status code {response.status}", "red")
                    return

        except Exception as e:
            cprint(f"[ERROR] in sendErrorMessage(): {e}", "red")
            return