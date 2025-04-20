import re
import requests
import logging
import subprocess
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class InfoResolverWebsite:
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_REGEX = re.compile(
        r"\(?\b\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"  # e.g., (123) 456-7890 or 123-456-7890
    )

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def extract_emails(self, html: str) -> list[str]:
        return list(set(self.EMAIL_REGEX.findall(html)))

    def extract_phones(self, html: str) -> list[str]:
        return list(set(self.PHONE_REGEX.findall(html)))

    def resolve(self, urls: list[str]) -> dict:
        all_emails = set()
        all_phones = set()

        for url in urls:
            try:
                response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()

                all_emails.update(self.extract_emails(text))
                all_phones.update(self.extract_phones(text))

            except Exception as e:
                self.logger.warning(f"❌ requests failed for {url}: {e}. Trying Selenium fallback...")

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
                    driver.get(url)
                    time.sleep(2)

                    html = driver.page_source
                    all_emails.update(self.extract_emails(html))
                    all_phones.update(self.extract_phones(html))

                    driver.close()
                except Exception as se:
                    self.logger.warning(f"🛑 Selenium also failed for {url}: {se}")

        return {
            "emails": sorted(all_emails),
            "phones": sorted(all_phones),
        }