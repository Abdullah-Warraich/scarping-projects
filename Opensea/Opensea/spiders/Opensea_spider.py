import scrapy
import csv
import openpyxl
import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException
import undetected_chromedriver as uc


class OpenseaSpider(scrapy.Spider):
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'HTTPERROR_ALLOW_ALL': True,
        'DEFAULT_REQUEST_HEADERS': {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
        },
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
    }
    start_urls = ['https://quotes.toscrape.com/']
    name = "Opensea_spider"

    def __init__(self, *args, **kwargs):
        super(OpenseaSpider, self).__init__(*args, **kwargs)
        # chrome_options = Options()
        # chrome_options.add_experimental_option("detach", True)
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option("useAutomationExtension", False)

        # options = uc.ChromeOptions()
        # chrome_opt = uc.ChromeOptions()
        # chrome_opt.add_argument('--disable-headless')
        # prefs = {"credentials_enable_service": False,
        #          "profile.password_manager_enabled": False}
        # chrome_opt.add_experimental_option("prefs", prefs)
        self.driver = uc.Chrome()
        # self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver.maximize_window()
        self.driver.get('https://opensea.io/rankings/trending?sortBy=one_day_volume')

    def parse(self, response, **kwargs):
        visited = []
        original_window = self.driver.current_window_handle
        visited_count = 0
        # detail_urls = []
        a = False
        while True:
            if a:
                if visited_count == len(visited):
                    break
            a = True
            sleep(2)
            visited_count = len(visited)
            WebDriverWait(self.driver, 25).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-c0dd234a-0 '
                                                          'sc-e7b51c31-0 ckCQsp fWxQZN"]'))
            )
            items = self.driver.find_elements(by=By.XPATH, value='//div[@class="sc-c0dd234a-0 '
                                                                 'sc-e7b51c31-0 ckCQsp fWxQZN"]')
            for item in items:
                detail_url = item.find_element(by=By.XPATH, value='./a').get_attribute('href')
                # detail_urls.append(detail_url)
                print(detail_url)
                collection = item.find_element(by=By.XPATH, value='.//div[@class="sc-48082a-0 bguyED"]').text
                if collection not in visited:
                    visited.append(collection)
                    item1 = dict()
                    item1['detail_url'] = detail_url
                    item1['Collection'] = collection
                    volume_floor_price = item.find_elements(by=By.XPATH, value='.//span[@class="text-md leading-'
                                                                               'md font-semibold text-primary"]/div')
                    item1['Volume'] = volume_floor_price[0].text
                    item1['Floor Price'] = volume_floor_price[1].text
                    green = item.find_elements(by=By.XPATH, value='.//span[@class="text-md leading-md font-semibold '
                                                                  'text-green-2"]/div')
                    red = item.find_elements(by=By.XPATH, value='.//span[@class="text-md leading-md font-semibold '
                                                                'text-red-2"]/div')
                    if green:
                        item1['% Change'] = green[0].text
                    elif red:
                        item1['% Change'] = red[0].text
                    item1['Sales'] = item.find_element(by=By.XPATH, value='.//div[@class="sc-c0dd234a-0 sc-8ed450db-0 s'
                                                                          'c-3d8bb57f-2 hhAa-dT cMkvCR"]/span/div').text
                    self.driver.switch_to.new_window('tab')
                    self.driver.get(item1['detail_url'])
                    links = self.driver.find_elements(by=By.XPATH, value='//div[@class="sc-c0dd234a-0 sc-630fc9ab-0 '
                                                                         'sc-968937a5-0 ckCQsp bNkKFC cNAoge"]/a')
                    links_list = []
                    for link in links:
                        links_list.append(link.get_attribute('href'))

                    item1['Social_Media_Links'] = ', '.join(links_list)

                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    # link.send_keys(Keys.CONTROL + Keys.RETURN)
                    # self.driver.switch_to.window(self.driver.window_handles[1])

                    yield item1

            self.driver.execute_script("window.scrollBy(0, 500);")
            print('Count: ', len(visited))
        self.driver.quit()
