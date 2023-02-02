import os
import re
import sys
from types import NoneType
from urllib.parse import parse_qs, urlparse

from aiohttp.client import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from bs4 import BeautifulSoup

from lib.multipartify import multipartify
from .browser import Browser
from .logger import Logger, LoggerType

admin_mapping = {
    os.getenv('ADMIN_1_URL'): {
        'auth_url': str(os.getenv('ADMIN_1_AUTH_URL')),
        'email': os.getenv('ADMIN_1_EMAIL'),
        'password': os.getenv('ADMIN_1_PASSWORD')
    },
    os.getenv('ADMIN_2_URL'): {
        'auth_url': os.getenv('ADMIN_2_AUTH_URL'),
        'email': os.getenv('ADMIN_2_EMAIL'),
        'password': os.getenv('ADMIN_2_PASSWORD')
    },
}


class AdminPanel:

    def __init__(self, session: ClientSession, admin_url: str):
        self.session = session
        self.admin_url = admin_url
        self.redirect_list = []
        self.browser = Browser()

    async def login(self):
        auth_url = admin_mapping[self.admin_url]['auth_url']
        Logger.log(LoggerType.LOG, 'Logging in, please wait...')

        token = await self._get_token(auth_url)
        payload = {
            'authenticity_token': token,
            'user': {
                'email': admin_mapping[self.admin_url]['email'],
                'password': admin_mapping[self.admin_url]['password'],
                'otp_attempt': ''
            },
            'password': {
                'visibility': '0'
            },
            'Commit': 'Sign In'
        }

        try:
            async with self.session.post(auth_url, data=multipartify(payload)) as res:
                html = await res.text()
                soup = BeautifulSoup(html, 'html.parser')
                user_html = soup.find('span', {'class': 'name'})

                if not user_html:
                    Logger.log(LoggerType.ERROR, 'Unable to login, possibly wrong credentials.', 'login()')
                    await self.exit()

                user = user_html.text
                if user == os.getenv('USR'):
                # if f'"{user}"' == os.getenv('USR'):
                    Logger.log(LoggerType.DONE, 'Logged in successfully.')

                else:
                    Logger.log(
                        LoggerType.ERROR,
                        f'Unable to check auth status, got {user}, expected to get {os.getenv("USR")}.',
                        'login()'
                    )
                    await self.exit()

        except Exception as e:
            Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', 'login()')
            await self.exit()

    async def get_return_url(self, tx_id: str):
        if tx_id:
            Logger.log(LoggerType.LOG, f'Working on {tx_id}...')
            try:
                async with self.session.get(f'{self.admin_url}?uid={tx_id}') as res:
                    html = await res.text()
                    logs = self._is_log(html)

                    if not logs:
                        Logger.log(LoggerType.WARN, f'Logs not found for {tx_id}.')
                        return

                    else:
                        self.redirect_list.clear()
                        return self._get_return_url_value(html)

            except Exception as e:
                Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', 'get_return_url()')
                await self.exit()

        else:
            Logger.log(LoggerType.WARN, 'Empty row.')

    async def get_redirect_list(self, return_url: str):
        if return_url:
            self.redirect_list.append(return_url)

            try:
                async with self.session.get(return_url, allow_redirects=False) as res:
                    next_url = res.headers.get('Location')
                    if next_url:
                        return await self.get_redirect_list(next_url)

                    else:
                        is_host = self._get_host(self.redirect_list[-1])
                        if is_host:
                            self.redirect_list.append(*is_host)
                        else:
                            url = self.browser.get_button_url(self.redirect_list[-1])
                            if url:
                                self.redirect_list.append(url)

                        return self.redirect_list

            except ClientConnectorError:
                return self.redirect_list
            except Exception as e:
                Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', 'get_redirect_list()')
                return self.redirect_list
            
    async def exit(self):
        await self.session.close()
        sys.exit()

    async def _get_token(self, auth_url: str):
        try:
            async with self.session.get(auth_url) as res:
                html = await res.text()
                soup = BeautifulSoup(html, 'html.parser')

                html_token = soup.find('input', {'name': 'authenticity_token'})
                if isinstance(html_token, NoneType):
                    Logger.log(LoggerType.ERROR, 'Unable to find token in markup.', '_get_token()')
                    await self.exit()

                token = html_token.get('value')
                if not token:
                    Logger.log(LoggerType.ERROR, 'Token found in markup, but unable to get its value.', '_get_token()')
                    await self.exit()

                return token

        except ClientConnectorError:
            Logger.log(LoggerType.ERROR, f'Unable to connect to {auth_url}.', '_get_token()')
            await self.exit()
        except Exception as e:
            Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', '_get_token()')
            await self.exit()

    @staticmethod
    def _is_log(html: str):
        soup = BeautifulSoup(html, 'html.parser')
        alert = soup.find('div', {'class': 'alert-message'}).text
        log_count = int(alert.split(' ')[0])
        return log_count

    @staticmethod
    def _get_return_url_value(html: str):
        try:
            return re.search('(?s)(?<=return_url&quot;=&gt;&quot;).*?(?=&quot;)', html).group()

        except Exception as e:
            Logger.log(LoggerType.WARN, f'Return url not found, {e}.', '_get_return_url_value()')

    @staticmethod
    def _get_host(url: str):
        parsed_url = urlparse(url)
        try:
            return parse_qs(parsed_url.query)['host']
        except KeyError:
            return
        except Exception as e:
            Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', '_get_host()')
