import os

from dotenv import load_dotenv

load_dotenv()

apiUrl = os.getenv("URL")
ssKey = os.getenv("SS_KEY")
tgToken = os.getenv("TG_TOKEN")
tgChat = os.getenv("TG_CHAT")