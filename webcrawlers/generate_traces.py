# https://selenium-python.readthedocs.io/installation.html#drivers

###########
# Imports #
###########

import sys
import time
import os
import subprocess
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

from capture_traffic import capture_traffic

##########################
# Handling CLI arguments #
##########################

try:
    OS = sys.argv[1] # "windows", "linux"
    IP = sys.argv[2] 
    INTERFACE = sys.argv[3]
except:
    print("Specify 3 arguments: [1] = OS, [2] = IPv4, [3] = Interface")
    exit(0)

#####################################################
# Specifying webdriver paths and Capture parameters #
#####################################################

chromedriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "chromedriver")
edgedriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "msedgedriver")
firefoxdriverpath = os.path.join(os.getcwd(), OS + "/webdrivers", "geckodriver")
if OS == "windows":
    chromedriverpath += ".exe"
    edgedriverpath += ".exe"
    firefoxdriverpath += ".exe"

OUTPUT_DIR = os.path.join(os.getcwd(), OS + "/traces/streaming_HTTP")

# You cannot directly filter OpenVPN protocols while capturing. However, if you know the UDP or TCP port used (see above), you can filter on that one.
FILTER = f"src host {IP} and udp port 1194"  

#####################
# Generating traces #
#####################

def flush_dns():
    pass 
    # if OS == "linux":
    #     subprocess.run(["systemd-resolve", "--flush-caches"])
    # elif OS == "windows":
    #     subprocess.run(["ipconfig", "/flushdns"])


# Firefox
for i in range(0):
    # flush dns
    flush_dns()
    # init driver
    service = FirefoxService(firefoxdriverpath)
    options = FirefoxOptions()
    options.headless = True # do not open browser GUI
    driver = webdriver.Firefox(options=options, service=service)
    # capture traffic
    output_file = os.path.join(OUTPUT_DIR, "firefox" + str(i+1) + ".pcapng")
    capture_traffic(driver, INTERFACE, FILTER, output_file, browsing=True)
    driver.quit()

# Chrome
for i in range(0):
    # flush dns
    flush_dns()
    # init driver   
    service = ChromeService(chromedriverpath)
    options = ChromeOptions()
    # options.headless = True # do not open browser GUI
    driver = webdriver.Chrome(options=options, service=service)
    # capture traffic
    output_file = os.path.join(OUTPUT_DIR, "chrome" + str(i+1) + ".pcapng")
    capture_traffic(driver, INTERFACE, FILTER, output_file, browsing=True)
    driver.quit()

# Edge
for i in range(3):
    # flush dns
    flush_dns()
    # init driver
    service = EdgeService(edgedriverpath)
    options = EdgeOptions()
    if OS == "windows":
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.headless = True # do not open browser GUI
    driver = webdriver.Edge(options=options, service=service)
    # capture traffic
    output_file = os.path.join(OUTPUT_DIR, "edge" + str(i+1) + ".pcapng")
    capture_traffic(driver, INTERFACE, FILTER, output_file, browsing=True)
    driver.quit()
