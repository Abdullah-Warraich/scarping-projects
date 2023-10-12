import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BooksSpider(scrapy.Spider):
    name = "Books_spider"
    base_url = "https://books.toscrape.com/"
    start_urls = ["https://books.toscrape.com/"]
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
        super(BooksSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.get(self.start_urls[0])

    def parse(self, response, **kwargs):
        detail_page_links = []
        page = True
        while page:
            links = self.driver.find_elements(by=By.XPATH, value="//li[@class='col-xs-6 "
                                                                 "col-sm-4 col-md-3 col-lg-3']/article/h3/a")
            detail_page_links.extend([link.get_attribute('href') for link in links])
            print(detail_page_links)

            next_page = self.driver.find_elements(by=By.XPATH, value='//li[@class = "next"]/a')
            if not next_page:
                page = False
            else:
                next_page[0].click()

        for detail_url in detail_page_links:
            print(detail_url)
            self.driver.get(detail_url)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class = "item active"]/img')
                )
            )
            item = dict()
            item['img_link'] = self.driver.find_element(by=By.XPATH, value='//img').get_attribute('src')
            item['name'] = self.driver.find_element(by=By.XPATH, value='//div[@class="col-sm-6 product_main"]/h1').text
            item['price'] = self.driver.find_element(by=By.XPATH, value="//div[@class='col-sm-6 "
                                                                        "product_main']/p[@class ='price_color']").text
            breadcrumb = self.driver.find_elements(by=By.XPATH, value="//ul[@class = 'breadcrumb']/li")
            item['breadcrumb'] = ' > '.join([b.text for b in breadcrumb])
            item['description'] = self.driver.find_element(by=By.XPATH, value='//article/p').text
            details = self.driver.find_elements(by=By.XPATH, value='//table/tbody/tr')
            for detail in details:
                value = detail.find_element(by=By.XPATH, value='./td').text
                col_name = detail.find_element(by=By.XPATH, value='./th').text
                item[col_name] = value
            yield item

        self.driver.quit()
