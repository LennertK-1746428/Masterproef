import requests 
import selenium 
import os
import re  
import time 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Services 
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService

# Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


def extract_urls(body):
        """
        gathers links to be visited in the future from a web page's body.
        does it by finding "href" attributes in the DOM
        :param body: the HTML body to extract links from
        :param root_url: the root URL of the given body
        :return: list of extracted links
        """
        pattern = r"href=[\"'](?!#)(.*?)[\"'].*?"  # ignore links starting with #, no point in re-visiting the same page
        urls = re.findall(pattern, body)
        return urls 


# Selenium
chromedriverpath = os.path.join(os.pardir, "webcrawlers/windows/webdrivers", "chromedriver.exe")
service = ChromeService(chromedriverpath)
options = ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2}) 
# options.headless = True # do not open browser GUI
driver = webdriver.Chrome(options=options, service=service)
driver.get("https://www.twitch.tv/")
time.sleep(20)
driver.quit()

exit(0)

s_urls = set(extract_urls("".join(driver.page_source)))
    

# Requests
response = requests.get("https://www.uhasselt.be", timeout=5)
r_urls = set(extract_urls(str(response.content)))

if s_urls == r_urls:
    print("Equal")
else:
    print(f"Saddd, len s = {len(s_urls)}, len r = {len(r_urls)}")

# with open("out.txt", "w") as f:
#     f.write(str(s_urls))



