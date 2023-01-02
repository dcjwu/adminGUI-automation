import os

from bs4 import BeautifulSoup

def isAuth(html):
    soup = BeautifulSoup(html, 'html.parser')
    userName = soup.find("span", {"class": "name"}).text

    if userName == os.getenv("USER"):
        return True
    else:
        return False
