import os

from dotenv import load_dotenv

load_dotenv()

apiUrl = os.getenv("URL")
ssKey = os.getenv("SS_KEY")