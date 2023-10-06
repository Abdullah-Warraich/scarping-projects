import csv
import openpyxl
import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException


class GoogleSpider(scrapy.Spider):
    name = "Google_Maps_spider"
    base_url = "https://books.toscrape.com/"
    start_urls = []
    driver = None
    custom_settings = {
        'FEED_EXPORTERS': {
            'xlsx': 'scrapy_xlsx.XlsxItemExporter',
        },
        'FEEDS': {
            'output.xlsx': {
                'format': 'xlsx',
                'overwrite': True,
            },
        },
    }

    def __init__(self, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)

        # Replace 'your_file.xlsx' with the path to your Excel file
        file_path = r"C:\Users\PMLS\Music\Projects\Google_Maps_selenium\quries.xlsx"

        workbook = openpyxl.load_workbook(file_path)

        sheet_name = 'Sheet1'  # Replace with the name of your sheet
        sheet = workbook[sheet_name]

        # Iterate through the rows and columns of the selected sheet
        for row in sheet.iter_rows(values_only=True):
            print(row[0])
            self.start_urls.append(f"https://www.google.com/maps/search/{row[0].replace(' ', '+')}")
        print(self.start_urls)
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def parse(self, response, **kwargs):
        for url in self.start_urls:
            self.driver.get(url)
            visited = []
            a = True
            b = 0
            while a:
                b += 1
                value = self.driver.find_elements(by=By.XPATH, value="//span[contains(text(), 'reached the end "
                                                                     "of the list')]")
                print(value)

                if value or b == 500:
                    a = False
                else:
                    scrollable_element = self.driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/'
                                                                                     'div[2]/div/div[1]/div/'
                                                                                     'div/div[2]/div[1]')
                    self.driver.execute_script("arguments[0].scrollTop += 500;", scrollable_element)

            sleep(2)
            links = self.driver.find_elements(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div'
                                                                 '/div/div[2]/div[1]/div/div/a')
            for link in links:
                if link.get_attribute('href') not in visited:
                    visited.append(link.get_attribute('href'))
                    try:
                        self.driver.execute_script("arguments[0].click();", link)
                        sleep(4)
                        item = dict()
                        item['name'] = ''
                        WebDriverWait(self.driver, 25).until(
                            EC.presence_of_element_located((By.XPATH, '//h1[@class="DUwDvf lfPIob"]'))
                        )
                        item['name'] = self.driver.find_element(by=By.XPATH, value='//h1[@class="DUwDvf lfPIob"]').text
                        print(item['name'])

                        item['ratings'] = ''
                        ratings = self.driver.find_elements(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[3]//'
                                                                               'div[2]/div/div[1]/div[2]/div/div[1]/'
                                                                               'div[2]/span[1]/span[1]')
                        if ratings:
                            print(ratings[0].text)
                            item['ratings'] = ratings[0].text
                        else:
                            print('No ratings found')
                        item['review_count'] = ''
                        review_count = self.driver.find_elements(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]//div/div[1]'
                                                                                    '/div[2]/span[2]/span/span')
                        if review_count:
                            item['review_count'] = review_count[0].text.strip('()')

                        buttons = self.driver.find_elements(by=By.XPATH, value='//div[contains(@aria-label, '
                                                                               '"Information for ")]/div/button')
                        links = self.driver.find_elements(by=By.XPATH, value='//div[contains(@aria-label, "Information for ")]/div'
                                                                             '/a[@aria-label != "Claim this business"]')
                        item['website_link'] = ''
                        item['location'] = ''
                        item['number'] = ''
                        item['reviews'] = ''

                        if links:
                            item['website_link'] = links[0].get_attribute('href')
                        for button in buttons:
                            img_link = button.find_element(by=By.XPATH, value='.//img').get_attribute('src')
                            if 'place_gm_blue' in img_link:
                                item['location'] = button.find_element(by=By.XPATH, value='.//div[@class="Io6YTe '
                                                                                          'fontBodyMedium kR99db "]').text
                            elif 'phone_gm_blue' in img_link:
                                item['number'] = button.find_element(by=By.XPATH, value='.//div[@class="Io6YTe '
                                                                                        'fontBodyMedium kR99db "]').text
                        print(len(links), len(buttons))
                        if item['review_count']:
                            scrollable = self.driver.find_element(by=By.XPATH, value='//div[@class="m6QErb DxyBCb '
                                                                                     'kA9KIf dS8AEf "]')
                            self.driver.execute_script("arguments[0].scrollTop += 1000;", scrollable)

                            WebDriverWait(self.driver, 25).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="jftiEf fontBodyMedium "]'))
                            )
                            print('We can now scrap reviews ', item['review_count'])
                            if int(item['review_count']) <= 3:
                                reviews = self.driver.find_elements(by=By.XPATH, value='//div[@class="jftiEf '
                                                                                       'fontBodyMedium "]')
                                rev = []
                                for review in reviews:
                                    name = review.find_element(by=By.XPATH, value='.//div[@class="d4r55 "]').text
                                    rate = review.find_elements(by=By.XPATH, value='.//img[@class="hCCjke vzX5Ic"]')
                                    rev.append(f"{name}: {len(rate)}")

                                item['reviews'] = ', '.join(rev)
                            else:
                                WebDriverWait(self.driver, 25).until(
                                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'More reviews')]"))
                                )
                                more_reviews = self.driver.find_element(by=By.XPATH, value="//span[contains(text(), "
                                                                                           "'More reviews')]")
                                self.driver.execute_script("arguments[0].click();", more_reviews)
                                WebDriverWait(self.driver, 20).until(
                                    EC.presence_of_element_located((By.XPATH, '//div[@class="jftiEf fontBodyMedium "]'))
                                )
                                reviews = self.driver.find_elements(by=By.XPATH, value='//div[@class="jftiEf '
                                                                                       'fontBodyMedium "]')
                                while len(reviews) < int(item['review_count'])-1:
                                    print(len(reviews))
                                    scrollable = self.driver.find_element(by=By.XPATH, value='//div[@class="m6QErb DxyBCb '
                                                                                             'kA9KIf dS8AEf "]')
                                    self.driver.execute_script("arguments[0].scrollTop += 500;", scrollable)
                                    WebDriverWait(self.driver, 5).until(
                                        EC.presence_of_element_located((By.XPATH, '//div[@class="jftiEf fontBodyMedium "]'))
                                    )
                                    reviews = self.driver.find_elements(by=By.XPATH, value='//div[@class="jftiEf '
                                                                                           'fontBodyMedium "]')
                                reviews = self.driver.find_elements(by=By.XPATH, value='//div[@class="jftiEf '
                                                                                       'fontBodyMedium "]')
                                for review in reviews:
                                    item['reviews'] += ', '
                                    WebDriverWait(self.driver, 25).until(
                                        EC.presence_of_element_located((By.XPATH, './/div[@class="d4r55 "]'))
                                    )
                                    item['reviews'] += review.find_element(by=By.XPATH, value='.//div[@class="'
                                                                                              'd4r55 "]').text
                                rev = []
                                for review in reviews:
                                    name = review.find_element(by=By.XPATH, value='.//div[@class="d4r55 "]').text
                                    rate = review.find_elements(by=By.XPATH, value='.//img[@class="hCCjke vzX5Ic"]')
                                    rev.append(f"{name}: {len(rate)}")

                                item['reviews'] = ', '.join(rev)
                        yield item
                    except TimeoutException:
                        self.driver.execute_script("arguments[0].click();", link)
                        sleep(3)
                    except StaleElementReferenceException:
                        sleep(2)
                        self.driver.execute_script("arguments[0].click();", link)
                        sleep(4)
                        WebDriverWait(self.driver, 25).until(
                            EC.presence_of_element_located((By.XPATH, '//h1[@class="DUwDvf lfPIob"]'))
                        )
                    except ElementClickInterceptedException:
                        print('Element is not clickable')
        self.driver.quit()

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(GoogleSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    #     return spider

    # def spider_closed(self):
    #     print(self.start_urls)
    #     if len(self.start_urls) >= 2:
    #         self.start_urls.pop(0)
    #         self.driver.get(self.start_urls[0])
    #     else:
    #         self.driver.quit()
    #         print('Closing Code!')


