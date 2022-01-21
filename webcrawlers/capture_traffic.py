import time
import subprocess
from selenium.webdriver.common.by import By

STREAMING_INTERVAL = 60
BROWSING_PAUSE_INTERVAL = 2


def browsing_traffic(driver, iface, filter, output_file):
    """ Generate browsing traffic """

    # start capturing
    capture_process = subprocess.Popen(args=["tshark", "-i", iface, "-w", output_file, "-f", filter])
    while capture_process.poll() is not None: # while process not alive yet
        print("tshark not started yet..")

    # capture browsing traffic
    driver.get("https://www.uhasselt.be")
    time.sleep(BROWSING_PAUSE_INTERVAL)
    driver.find_element(By.XPATH, '//a[@href="/UH/nl/InfoVoor/studenten-en-doctorandi.html"]').click()
    time.sleep(BROWSING_PAUSE_INTERVAL)
    driver.find_element(By.XPATH, '//a[@href="/"]').click()
    time.sleep(BROWSING_PAUSE_INTERVAL) 
    driver.find_element(By.XPATH, '//a[@href="/UH/nl/InfoVoor/InfoVoor-Sollicitanten.html"]').click()
    time.sleep(BROWSING_PAUSE_INTERVAL) 

    # terminate capturing
    capture_process.terminate()
    while capture_process.poll() is None: # while process alive
        print("tshark not terminated yet..")
        time.sleep(1)


def streaming_traffic(driver, iface, filter, output_file):
    """ Generate streaming traffic """

    # open streaming link
    driver.get("https://youtu.be/dQw4w9WgXcQ")  
    time.sleep(10)   # make sure streaming has already begun
    
    # start capturing when already streaming
    capture_process = subprocess.Popen(args=["tshark", "-i", iface, "-w", output_file, "-f", filter])

    # capture streaming
    time.sleep(STREAMING_INTERVAL)

    # terminate capturing
    capture_process.terminate()
    while capture_process.poll() is None: # while process alive
        print("tshark not terminated yet..")
        time.sleep(1)


def capture_traffic(driver, iface, filter, output_file, browsing=False, streaming=False):
    """ Handle the actions to generate traffic """

    # do actions
    if browsing:
        browsing_traffic(driver, iface, filter, output_file)
    elif streaming:
        streaming_traffic(driver, iface, filter, output_file)

        
