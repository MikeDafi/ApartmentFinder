import subprocess
import time
import urllib.parse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class WebsiteResolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def resolve(self, name: str) -> list[str]:
        """
        Open the system-installed Chrome and use Selenium to get up to 3 result URLs.
        Returns a list of external URLs.
        """
        query = urllib.parse.quote_plus(name)
        search_url = f"https://www.google.com/search?q={query}"
        urls = []

        try:
            subprocess.Popen([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--remote-debugging-port=9222",
                "--user-data-dir=/tmp/chrome-debug"
            ])
            time.sleep(2)

            options = Options()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            driver.get(search_url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
            )

            for link in driver.find_elements(By.CSS_SELECTOR, "a"):
                href = link.get_attribute("href")
                if href and "google.com" not in href and href.startswith("http"):
                    urls.append(href)
                if len(urls) == 3:
                    break

            driver.close()  # Close only the current tab
        except Exception as e:
            self.logger.warning(f"Website resolution failed for '{name}': {e}")

        return urls