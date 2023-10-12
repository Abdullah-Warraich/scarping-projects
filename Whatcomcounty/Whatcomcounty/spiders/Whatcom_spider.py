from time import sleep

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Keys


class WhatcomSpider(scrapy.Spider):
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
    name = "Whatcom_spider"

    def __init__(self, *args, **kwargs):
        super(WhatcomSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.get('https://recording.whatcomcounty.us/')

    def parse(self, response, **kwargs):
        documents = ['Assignment of Deed of Trust', 'Appointment of Trustee', 'Lis Pendens',
                     'Trustee Sale - Residential', 'Judgment', 'Notice', 'Lien']
        self.driver.find_element(by=By.XPATH, value='//button[@class= "btn btn-default"]').click()
        self.driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Advanced Search')]").click()
        while documents:
            doc_name = documents.pop(0)
            self.driver.implicitly_wait(5)
            self.driver.find_element(by=By.XPATH, value='//input[@id="Criteria_Filter_RecordingDateStart'
                                                        '"]').send_keys('01/01/2023')
            date = datetime.now().date()
            print(date)
            self.driver.find_element(by=By.XPATH, value='//input[@id="Criteria_Filter_RecordingDateEnd"]'
                                                        '').send_keys(str(date.month)+"/"+str(date.day)+'/'+str(date.year))
            document_type = Select(self.driver.find_element(by=By.XPATH, value='//select[@id="Filter_DocumentSubtype"]'))
            document_type.select_by_visible_text(doc_name)
            self.driver.find_element(by=By.XPATH, value='//button[@id="adv-search-btn"]').click()
            # self.driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Show 500')]").click()
            pages = True
            while pages:
                records = self.driver.find_elements(by=By.XPATH, value='//div[@class="table search-result"]')
                original_window = self.driver.current_window_handle
                for record in records:
                    item = dict()
                    date_type = record.find_elements(by=By.XPATH, value='.//span[@class="inline margin-right"]')
                    doc_type = date_type[1].text.split(':')[1]
                    if 'Appointment of Trustee' in doc_type:
                        if 'Reconveyance' in doc_type:
                            continue
                        else:
                            references = record.find_elements(by=By.XPATH, value='.//a[@title="View Reference"]')
                            if references:
                                actions = ActionChains(self.driver)
                                actions.key_down(Keys.CONTROL).click(references[0]).key_up(Keys.CONTROL).perform()
                                sleep(1)
                                self.driver.switch_to.window(self.driver.window_handles[-1])
                                text = self.driver.find_element(by=By.XPATH, value='//*[@id="tab_1"]/div[4]/a[1]/div/'
                                                                                   'div[2]/div').text
                                sleep(5)
                                self.driver.close()
                                self.driver.switch_to.window(original_window)
                                print(text)
                                if 'Reconveyance' in text:
                                    continue

                    item['Instrument No'] = record.find_element(by=By.XPATH, value='.//a[@class = "recording-link"]').text

                    item['Date Recorded'] = date_type[0].text.split(':')[1:]
                    item['Doc Type'] = date_type[1].text.split(':')[1]
                    item['Detail_url'] = record.find_element(by=By.XPATH, value='.//a[@class = "recording-li'
                                                                                'nk"]').get_attribute('href')
                    grant = record.find_elements(by=By.XPATH, value='.//div[@class="pull-left margin-left margin-right"]')
                    item['Grantor'] = '| '.join([grantor.text.split(':')[-1] for grantor in grant[0].
                                                 find_elements(by=By.XPATH, value='./div')])
                    item['Grantee'] = '| '.join([grantee.text.split(':')[-1] for grantee in grant[1].
                                                 find_elements(by=By.XPATH, value='./div')])
                    item['Legal Description'] = ''
                    item['Parcel No'] = ''
                    parcel_no = []
                    spans = record.find_elements(by=By.XPATH, value='.//div[2]/div/div[3]/div')
                    if spans:
                        for span in spans[0].find_elements(by=By.XPATH, value='./span'):
                            if span.find_element(by=By.XPATH, value='./label').text == 'Plat':
                                item['Legal Description'] = span.find_element(by=By.XPATH, value='./span').text
                            if span.find_element(by=By.XPATH, value='./label').text  == 'APN#':
                                parcel_no.append(span.find_element(by=By.XPATH, value='./span').text)
                        item['Parcel No'] = ' | '.join(parcel_no)
                    if not parcel_no:
                        print('hello world')

                        references = record.find_elements(by=By.XPATH, value='.//a[@title="View Reference"]')
                        if references:
                            actions = ActionChains(self.driver)
                            actions.key_down(Keys.CONTROL).click(references[0]).key_up(Keys.CONTROL).perform()
                            sleep(1)
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            parcel = self.driver.find_elements(by=By.XPATH, value='//*[@id="tab_1"]/div[2]/div/table/'
                                                                                  'tbody/tr/td[1]')
                            if parcel:
                                item['Parcel No'] = parcel[0].text
                            sleep(5)
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                    yield item
                pages = False
                if not self.driver.find_elements(by=By.XPATH, value='//button[@title = "Next 50" and not(@disabled)]'):
                    pages = False
                else:
                    self.driver.find_element(by=By.XPATH, value='//button[@title = "Next 50" and not(@disabled)]').click()
                if doc_name:
                    self.driver.find_element(by=By.XPATH, value="//a[text() = 'New Search']").click()
        self.driver.quit()
