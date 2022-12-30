from termcolor import cprint

from lib.sendErrorMessage import sendErrorMessage

async def unpackList(item, id = None):
    try:
        return item[0]
    except Exception as e:
        cprint(f"[ERROR] in unpackList: {e}", "red")
        await sendErrorMessage(f"[ERROR] in unpackList: Unable to handle data - {item} ({type(item)}). TX ID {id}.")
        return