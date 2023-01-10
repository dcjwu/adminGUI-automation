import os
import sys

import inquirer

from bs4 import BeautifulSoup

from aiohttp.client import ClientSession

from app.logger.logger import Logger, LoggerType

from lib.multipartify import multipartify

admin_mapping = {
    os.getenv("ADMIN_1_URL"): {
        "auth_url": os.getenv("ADMIN_1_AUTH_URL"),
        "email": os.getenv("ADMIN_1_EMAIL"),
        "password": os.getenv("ADMIN_1_PASSWORD")
    },
    os.getenv("ADMIN_2_URL"): {
        "auth_url": os.getenv("ADMIN_2_AUTH_URL"),
        "email": os.getenv("ADMIN_2_EMAIL"),
        "password": os.getenv("ADMIN_2_PASSWORD")
    },
}


class AdminPanel:
    def __init__(self, session: ClientSession) -> None:
        self.session = session
        self.admin_url = None
        self.token = None
        self.auth_url = None

    def get_url(self):
        q = [inquirer.List("admin_url", message="Please, choose URL", choices=list(admin_mapping.keys()))]
        a = inquirer.prompt(q)
        self.admin_url = a["admin_url"]

    async def get_auth_token(self):
        self.auth_url = admin_mapping[self.admin_url]["auth_url"]
        try:
            async with self.session.get(self.auth_url) as res:
                html = await res.text()
                soup = BeautifulSoup(html, "html.parser")
                self.token = soup.find("input", {"name": "authenticity_token"}).get("value")
                Logger.log(LoggerType.LOG, "Auth token received.")
        except Exception as e:
            Logger.log(LoggerType.ERROR, f"Unable to get auth token, please contact Admin, {e}.", "get_auth_token()")
            sys.exit()

    async def login(self):
        payload = {
            "authenticity_token": self.token,
            "user": {
                "email": admin_mapping[self.admin_url]["email"],
                "password": admin_mapping[self.admin_url]["password"],
                "otp_attempt": ""
            },
            "password": {
                "visibility": "0"
            },
            "Commit": "Sign In"
        }

        try:
            async with self.session.post(self.auth_url, data=multipartify(payload)) as res:
                html = await res.text()

                if self._is_auth(html):
                    Logger.log(LoggerType.LOG, "Logged in successfully!")
                else:
                    Logger.log(
                        LoggerType.ERROR, "Unable to check auth status, please contact Admin.", "login() -> is_auth()"
                    )
                    sys.exit()
        except Exception as e:
            Logger.log(
                LoggerType.ERROR,
                f"Unable to log in, seems like wrong credentials. Please, contact Admin, {e}.",
                "login()"
            )
            sys.exit()

    @staticmethod
    def _is_auth(html):
        soup = BeautifulSoup(html, "html.parser")
        user = soup.find("span", {"class": "name"}).text
        return user == os.getenv("USER")






