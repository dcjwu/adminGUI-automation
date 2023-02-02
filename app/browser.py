from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .logger import Logger, LoggerType


class Browser:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1140x969')
        chrome_options.add_argument('--disable-gpu')
        # driver_path = os.path.join(os.getcwd(), 'drivers/chromedriver-macos')
        # service = Service(executable_path=driver_path)
        # self.driver = webdriver.Chrome(options=chrome_options, service=service)
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_button_url(self, url: str):
        self.driver.get(url)
        try:
            btn = WebDriverWait(
                driver=self.driver,
                timeout=1.5,
            ).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[type=button]')))
            btn.click()
            return self.driver.current_url

        except TimeoutException:
            Logger.log(LoggerType.WARN, 'Button location TIMEOUT.')
        except Exception as e:
            Logger.log(LoggerType.ERROR, f'Unexpected error, please contact Admin, {e}.', 'get_button_url()')

    def quit(self):
        self.driver.quit()
