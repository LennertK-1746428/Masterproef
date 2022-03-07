import argparse
import datetime
import json
import logging
import random
import re
import sys
import time
import os 
import subprocess

from urllib3.exceptions import LocationParseError

try:                 # Python 2
    from urllib.parse import urljoin, urlparse
except ImportError:  # Python 3
    from urlparse import urljoin, urlparse

try:                 # Python 2
    reload(sys)
    sys.setdefaultencoding('latin-1')
except NameError:    # Python 3
    pass


from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Crawler(object):
    def __init__(self, driver):
        """
        Initializes the Crawl class
        """
        self._config = {}
        self._links = []
        self._start_time = None
        self._driver = driver 

    class CrawlerTimedOut(Exception):
        """
        Raised when the specified timeout is exceeded
        """
        pass

    def _request(self, url):
        """
        Sends a POST/GET requests using a random user agent
        :param url: the url to visit
        :return: the response Requests object
        """
        # random_user_agent = random.choice(self._config["user_agents"])
        # headers = {'user-agent': random_user_agent}
        # response = requests.get(url, timeout=5)
        self._driver.get(url)
        time.sleep(0.5)
        return "".join(self._driver.page_source)

    @staticmethod
    def _normalize_link(link, root_url):
        """
        Normalizes links extracted from the DOM by making them all absolute, so
        we can request them, for example, turns a "/images" link extracted from https://imgur.com
        to "https://imgur.com/images"
        :param link: link found in the DOM
        :param root_url: the URL the DOM was loaded from
        :return: absolute link
        """
        try:
            parsed_url = urlparse(link)
        except ValueError:
            # urlparse can get confused about urls with the ']'
            # character and thinks it must be a malformed IPv6 URL
            return None
        parsed_root_url = urlparse(root_url)

        # '//' means keep the current protocol used to access this URL
        if link.startswith("//"):
            return "{}://{}{}".format(parsed_root_url.scheme, parsed_url.netloc, parsed_url.path)

        # possibly a relative path
        if not parsed_url.scheme:
            return urljoin(root_url, link)

        return link

    @staticmethod
    def _is_valid_url(url):
        """
        Check if a url is a valid url.
        Used to filter out invalid values that were found in the "href" attribute,
        for example "javascript:void(0)"
        taken from https://stackoverflow.com/questions/7160737
        :param url: url to be checked
        :return: boolean indicating whether the URL is valid or not
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def _is_blacklisted(self, url):
        """
        Checks is a URL is blacklisted
        :param url: full URL
        :return: boolean indicating whether a URL is blacklisted or not
        """
        return any(blacklisted_url in url for blacklisted_url in self._config["blacklisted_urls"])

    def _should_accept_url(self, url):
        """
        filters url if it is blacklisted or not valid, we put filtering logic here
        :param url: full url to be checked
        :return: boolean of whether or not the url should be accepted and potentially visited
        """
        return url and self._is_valid_url(url) and not self._is_blacklisted(url)

    def _extract_urls(self, body, root_url):
        """
        gathers links to be visited in the future from a web page's body.
        does it by finding "href" attributes in the DOM
        :param body: the HTML body to extract links from
        :param root_url: the root URL of the given body
        :return: list of extracted links
        """
        pattern = r"href=[\"'](?!#)(.*?)[\"'].*?"  # ignore links starting with #, no point in re-visiting the same page
        urls = re.findall(pattern, str(body))

        normalize_urls = [self._normalize_link(url, root_url) for url in urls]
        filtered_urls = list(filter(self._should_accept_url, normalize_urls))

        return filtered_urls

    def _remove_and_blacklist(self, link):
        """
        Removes a link from our current links list
        and blacklists it so we don't visit it in the future
        :param link: link to remove and blacklist
        """
        self._config['blacklisted_urls'].append(link)
        del self._links[self._links.index(link)]

    def _browse_from_links(self, depth=0):
        """
        Selects a random link out of the available link list and visits it.
        Blacklists any link that is not responsive or that contains no other links.
        Please note that this function is recursive and will keep calling itself until
        a dead end has reached or when we ran out of links
        :param depth: our current link depth
        """
        is_depth_reached = depth >= self._config['max_depth']
        if not len(self._links) or is_depth_reached:
            logging.debug("Hit a dead end, moving to the next root URL")
            # escape from the recursion, we don't have links to continue or we have reached the max depth
            return

        if self._is_timeout_reached():
            raise self.CrawlerTimedOut

        random_link = random.choice(self._links)
        try:
            logging.info("Visiting {}".format(random_link))
            sub_page = self._request(random_link)
            sub_links = self._extract_urls(sub_page, random_link)

            # sleep for a random amount of time
            time.sleep(random.randrange(self._config["min_sleep"], self._config["max_sleep"]))

            # make sure we have more than 1 link to pick from
            if len(sub_links) > 1:
                # extract links from the new page
                self._links = self._extract_urls(sub_page, random_link)
            else:
                # else retry with current link list
                # remove the dead-end link from our list
                self._remove_and_blacklist(random_link)

        # except requests.exceptions.RequestException:
        #     logging.debug("Exception on URL: %s, removing from list and trying again!" % random_link)
        #     self._remove_and_blacklist(random_link)
        except Exception as e:
            print(e)

        self._browse_from_links(depth + 1)

    def load_config_file(self, file_path):
        """
        Loads and decodes a JSON config file, sets the config of the crawler instance
        to the loaded one
        :param file_path: path of the config file
        :return:
        """
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
            self.set_config(config)

    def set_config(self, config):
        """
        Sets the config of the crawler instance to the provided dict
        :param config: dict of configuration options, for example:
        {
            "root_urls": [],
            "blacklisted_urls": [],
            "click_depth": 5
            ...
        }
        """
        self._config = config

    def set_option(self, option, value):
        """
        Sets a specific key in the config dict
        :param option: the option key in the config, for example: "max_depth"
        :param value: value for the option
        """
        self._config[option] = value

    def _is_timeout_reached(self):
        """
        Determines whether the specified timeout has reached, if no timeout
        is specified then return false
        :return: boolean indicating whether the timeout has reached
        """
        is_timeout_set = self._config["timeout"] is not False  # False is set when no timeout is desired
        end_time = self._start_time + datetime.timedelta(seconds=self._config["timeout"])
        is_timed_out = datetime.datetime.now() >= end_time

        return is_timeout_set and is_timed_out

    def crawl(self):
        """
        Collects links from our root urls, stores them and then calls
        `_browse_from_links` to browse them
        """
        self._start_time = datetime.datetime.now()

        while True:
            url = random.choice(self._config["root_urls"])
            try:
                body = self._request(url)
                self._links = self._extract_urls(body, url)
                logging.debug("found {} links".format(len(self._links)))
                self._browse_from_links()

            except MemoryError:
                logging.warn("Error: content at url: {} is exhausting the memory".format(url))

            except LocationParseError:
                logging.warn("Error encountered during parsing of: {}".format(url))

            except self.CrawlerTimedOut:
                logging.info("Timeout has exceeded, exiting")
                return
            
            except Exception as e:
                print(e)


def get_driver(args):
    driver = None

    if args.browser == "chrome":
        chromedriverpath = os.path.join(args.drivers_dir, "chromedriver")
        if args.os == "windows":
            chromedriverpath += ".exe"
        service = ChromeService(chromedriverpath)
        options = ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2}) 
        # options.headless = True # do not open browser GUI
        driver = webdriver.Chrome(options=options, service=service)

    elif args.browser == "edge":
        edgedriverpath = os.path.join(args.drivers_dir, "msedgedriver")
        if args.os == "windows":
            edgedriverpath += ".exe"
        service = EdgeService(edgedriverpath)
        options = EdgeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2}) 
        if args.os == "windows":
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.headless = True # do not open browser GUI
        driver = webdriver.Edge(options=options, service=service)
    
    elif args.browser == "firefox":
        firefoxdriverpath = os.path.join(args.drivers_dir, "geckodriver")
        if args.os == "windows":
            firefoxdriverpath += ".exe"
        service = FirefoxService(firefoxdriverpath)
        options = FirefoxOptions()
        options.add_argument("start-maximized")
        # options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2}) 
        # options.headless = True # do not open browser GUI
        driver = webdriver.Firefox(options=options, service=service)

    driver.maximize_window()
    return driver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', metavar='-l', type=str, help='logging level', default='info')
    parser.add_argument('--config', metavar='-c', required=True, type=str, help='config file')
    parser.add_argument('--timeout', metavar='-t', required=False, type=int,
                        help='for how long the crawler should be running, in seconds', default=False)
    parser.add_argument('--browser', metavar='-b', required=True, type=str, help='which browser')
    parser.add_argument('--os', metavar='-o', required=True, type=str, help='which OS')
    parser.add_argument('--interface', metavar='-i', required=True, type=str, help='which interface')
    parser.add_argument('--traffic', metavar='-i', required=True, type=str, help='which traffic')
    parser.add_argument('--drivers_dir', metavar='-i', required=True, type=str, help='where drivers')
    parser.add_argument('--output_dir', metavar='-i', required=True, type=str, help='where output')
    args = parser.parse_args()

    level = getattr(logging, args.log.upper())
    logging.basicConfig(level=level)
    
    # Driver 
    driver = get_driver(args)

    # Init Crawler
    crawler = Crawler(driver)
    crawler.load_config_file(args.config)
    if args.timeout:
        crawler.set_option('timeout', args.timeout)

    # Capture
    filter = "udp port 1194"
    capture_process = subprocess.Popen(args=["tshark", "-i", args.interface, "-w", f"{args.output_dir}/{args.os}-{args.browser}-{args.traffic}-{int(time.time())}.pcapng", "-f", filter])
    while capture_process.poll() is not None: # while process not alive yet
        print("tshark not started yet..")

    # browsing
    if args.traffic == "browsing":
        crawler.crawl()
    # streaming yt
    elif "youtube" in args.traffic:
        driver.get("https://youtu.be/knsnQzDVpcI")  
        # bypass cookie consent 
        consent_button_xpath = '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a'
        consent = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
        consent = driver.find_element_by_xpath(consent_button_xpath)
        consent.click()
        time.sleep(args.timeout)
    # streaming twitch
    else:
        driver.get("https://www.twitch.tv/topgeartv")  
        time.sleep(args.timeout)

    # terminate capturing
    capture_process.terminate()
    while capture_process.poll() is None: # while process alive
        print("tshark not terminated yet..")
        time.sleep(1)

    driver.quit()


if __name__ == '__main__':
    main()
