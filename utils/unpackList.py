from termcolor import cprint

from utils.sendErrorMessage import sendErrorMessage

async def unpackList(item, id = None):
    try:
        return item[0]
    except Exception as e:
        cprint(f"[ERROR] in unpackList(): {e}", "red")
        await sendErrorMessage(f"[ERROR] in unpackList(): Unexpected param - {item} ({type(item)}).\n TX: {id}")
        return