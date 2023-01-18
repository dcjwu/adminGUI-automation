import os
import sys
import re

import inquirer

from bs4 import BeautifulSoup

from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientConnectorError

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
        self.redirect_list = []

    def get_url(self):
        q = [
            inquirer.List(
                "admin_url",
                message="Please, choose URL",
                choices=list(admin_mapping.keys())
            )
        ]
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

    async def get_return_url(self, uid):
        Logger.log(LoggerType.LOG, f"Working on {uid}...")
        try:
            async with self.session.get(f"{self.admin_url}?uid={uid}") as res:
                html = await res.text()
                self.redirect_list.clear()
                try:
                    self._are_logs_available(html)
                    return self._find_return_url_value(html)
                except Exception as e:
                    Logger.log(LoggerType.WARN, e)

        except Exception as e:
            Logger.log(LoggerType.ERROR, f"Unable to get data for {uid}, {e}.", "get_return_url()")

    async def get_redirects(self, url):
        if url:
            self.redirect_list.append(url)
            try:
                async with self.session.get(url, allow_redirects=False) as res:
                    url = res.headers.get("Location")
                    if url:
                        return await self.get_redirects(url)
                    else:
                        Logger.log(LoggerType.LOG, f"Redirect flow: {' >> '.join(self.redirect_list)}")
                        return self.redirect_list
            except ClientConnectorError as e:
                Logger.log(LoggerType.WARN, e)
                Logger.log(LoggerType.LOG, f"Redirect flow: {' >> '.join(self.redirect_list)}")
                return self.redirect_list
            except Exception as e:
                Logger.log(
                    LoggerType.ERROR,
                    f"Unhandled exception, please check with Admin if this is ok {e}.", "go_to_return_url()"
                )
                Logger.log(LoggerType.LOG, f"Redirect flow: {' >> '.join(self.redirect_list)}")
                return self.redirect_list

    async def disconnect(self):
        await self.session.close()

    @staticmethod
    def _is_auth(html):
        soup = BeautifulSoup(html, "html.parser")
        user = soup.find("span", {"class": "name"}).text
        return user == os.getenv("USER")

    @staticmethod
    def _are_logs_available(html):
        soup = BeautifulSoup(html, "html.parser")
        value = soup.find("div", {"class": "alert-message"}).text
        count = int(value.split(" ")[0])
        if not count:
            raise Exception("Logs not found.")

    @staticmethod
    def _find_return_url_value(html):
        try:
            url_value = re.search("(?s)(?<=return_url&quot;=&gt;&quot;).*?(?=&quot;)", html).group()
            Logger.log(LoggerType.LOG, f"Return url found, {url_value}.")
            return url_value

        except Exception as e:
            Logger.log(LoggerType.ERROR, f"Unable to get return url, {e}.", "_find_return_url_value()")
