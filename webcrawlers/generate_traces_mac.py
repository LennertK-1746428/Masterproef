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
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.chrome.service import Service as ChromeService

# Options
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions


##########################
# Handling CLI arguments #
##########################

try:
    IP = sys.argv[1] 
    INTERFACE = sys.argv[2]
except:
    print("Specify 2 arguments: [1] = IPv4, [2] = Interface")


#####################################################
# Specifying webdriver paths and Capture parameters #
#####################################################

OS = "mac"
chromedriverpath = os.path.join(os.getcwd(), OS + "/webdrivers/chromedriver", "chromedriver")
OUTPUT_DIR = os.path.join(os.getcwd(), OS + "/traces/webbrowsers")
FILTER = f"src host {IP} and udp port 1194"  # You cannot directly filter OpenVPN protocols while capturing. However, if you know the UDP or TCP port used (see above), you can filter on that one.
PAUSE_INTERVAL = 2


#####################
# Generating traces #
#####################

def flush_dns():
    subprocess.run(["ipconfig", "/flushdns"]) # TODO: find MAC command
        

def webpage_actions(driver):
    driver.get("https://www.uhasselt.be")
    time.sleep(PAUSE_INTERVAL)
    driver.find_element(By.XPATH, '//a[@href="/UH/nl/InfoVoor/studenten-en-doctorandi.html"]').click()
    time.sleep(PAUSE_INTERVAL)
    #driver.find_element(By.XPATH, '//a[@href="/UH/nl/InfoVoor/TS1.html"]').click()
    driver.find_element(By.XPATH, '//a[@href="/"]').click()
    time.sleep(PAUSE_INTERVAL) 
    driver.find_element(By.XPATH, '//a[@href="/UH/nl/InfoVoor/InfoVoor-Sollicitanten.html"]').click()
    time.sleep(PAUSE_INTERVAL) 


# Safari
for i in range(3):
    # flush dns
    flush_dns()
    # init driver
    driver = webdriver.Safari()
    # start capturing
    output_file = os.path.join(OUTPUT_DIR, "safari" + str(i+1) + ".pcapng")
    capture_process = subprocess.Popen(args=["tshark", "-i", INTERFACE, "-w", output_file, "-f", FILTER])
    # do some stuff
    webpage_actions(driver)
    # close driver and terminate capturing
    driver.close()
    capture_process.terminate()


# Chrome
for i in range(3):
    # flush dns
    flush_dns()
    # init driver
    service = ChromeService(chromedriverpath)
    options = ChromeOptions()
    options.headless = True # do not open browser GUI
    driver = webdriver.Chrome(options=options, service=service)
    # start capturing
    output_file = os.path.join(OUTPUT_DIR, "chrome" + str(i+1) + ".pcapng")
    capture_process = subprocess.Popen(args=["tshark", "-i", INTERFACE, "-w", output_file, "-f", FILTER])
    # do some stuff
    webpage_actions(driver)
    # close driver and terminate capturing
    driver.close()
    capture_process.terminate()
