import time
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

STREAMING_INTERVAL = 40
BROWSING_PAUSE_INTERVAL = 2


def browsing_traffic(driver, iface, filter, output_file):
    """ Generate browsing traffic """

    # start capturing
    capture_process = subprocess.Popen(args=["tshark", "-i", iface, "-w", output_file, "-f", filter])
    while capture_process.poll() is not None: # while process not alive yet
        print("tshark not started yet..")

    # capture browsing traffic
    driver.get("https://www.uhasselt.be")
    driver.maximize_window()
    time.sleep(BROWSING_PAUSE_INTERVAL)
    driver.find_element(By.XPATH, '//*[@id="uhasselt-page"]/section[1]/div[1]/div[1]/div[2]/ul/li[2]/a').click()
    time.sleep(BROWSING_PAUSE_INTERVAL)
    driver.find_element(By.XPATH, '//*[@id="uhasselt-page"]/div[1]/nav/div/div[3]/ul/li[2]/a').click()
    time.sleep(BROWSING_PAUSE_INTERVAL) 
    driver.find_element(By.XPATH, '//*[@id="uhasselt-page"]/div[1]/nav/div/div[1]/a').click()
    time.sleep(BROWSING_PAUSE_INTERVAL) 
    driver.find_element(By.XPATH, '//*[@id="uhasselt-page"]/div[1]/nav/div/div[2]/ul[2]/li[3]/a').click()
    time.sleep(BROWSING_PAUSE_INTERVAL) 
    
    # terminate capturing
    capture_process.terminate()
    while capture_process.poll() is None: # while process alive
        print("tshark not terminated yet..")
        time.sleep(1)


def streaming_quic_traffic(driver, iface, filter, output_file):
    """ Generate streaming QUIC traffic (YouTube) """

    # open streaming link
    driver.get("https://youtu.be/dQw4w9WgXcQ")  
    driver.maximize_window()

    # bypass cookie consent 
    consent_button_xpath = '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a'
    consent = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
    consent = driver.find_element_by_xpath(consent_button_xpath)
    consent.click()

    time.sleep(5)   # make sure streaming has already begun
    
    # start capturing when already streaming
    #capture_process = subprocess.Popen(args=["tshark", "-i", iface, "-w", output_file, "-f", filter])

    # capture streaming
    time.sleep(STREAMING_INTERVAL)

    # terminate capturing
    # capture_process.terminate()
    # while capture_process.poll() is None: # while process alive
    #     print("tshark not terminated yet..")
    #     time.sleep(1)


def streaming_http_traffic(driver, iface, filter, output_file):
    """ Generate streaming HTTP traffic (Twitch) """

    # open streaming link
    driver.get("https://www.twitch.tv/ekuegan")  
    driver.maximize_window()

    time.sleep(5)   # make sure streaming has already begun
    
    # start capturing when already streaming
    capture_process = subprocess.Popen(args=["tshark", "-i", iface, "-w", output_file, "-f", filter])

    # capture streaming
    time.sleep(STREAMING_INTERVAL)

    # terminate capturing
    capture_process.terminate()
    while capture_process.poll() is None: # while process alive
        print("tshark not terminated yet..")
        time.sleep(1)


def capture_traffic(driver, iface, filter, output_file, browsing=False, streaming_quic=False, streaming_http=False):
    """ Handle the actions to generate traffic """

    # do actions
    if browsing:
        browsing_traffic(driver, iface, filter, output_file)
    elif streaming_quic:
        streaming_quic_traffic(driver, iface, filter, output_file)
    elif streaming_http:
        streaming_http_traffic(driver, iface, filter, output_file)



        
