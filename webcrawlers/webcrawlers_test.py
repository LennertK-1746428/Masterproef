# https://selenium-python.readthedocs.io/installation.html#drivers

###########
# Imports #
###########

import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Services (same can be done with Options)
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

####################
# Testing browsers #
####################

OS = "linux"

# webdriver paths
chromedriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "chromedriver")
edgedriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "msedgedriver")
firefoxdriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "geckodriver")
if OS == "windows":
    chromedriverpath += ".exe"
    edgedriverpath += ".exe"
    firefoxdriverpath += ".exe"


PAUSE_INTERVAL = 2
def webpage_actions(driver):
    driver.get("https://www.uhasselt.be")
    time.sleep(PAUSE_INTERVAL)


# Chrome
service = ChromeService(chromedriverpath)
driver = webdriver.Chrome(service=service)
# driver.get("http://www.python.org")
webpage_actions(driver)
driver.close()

if OS == "mac":
    # Safari
    driver = webdriver.Safari()
    webpage_actions(driver)
    driver.close()
    exit(0)

# Firefox
service = FirefoxService(firefoxdriverpath)
driver = webdriver.Firefox(service=service)
webpage_actions(driver)
driver.close()

# Edge
service = EdgeService(edgedriverpath)
options = EdgeOptions()
if OS == "windows":
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(service=service, options=options)
webpage_actions(driver)
driver.close()