from urllib.parse import urljoin
import scrapy
import string
from itertools import product


class SirconSpider(scrapy.Spider):
    name = "sircon_spider"
    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0.2,
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
    }
    state = ''
    pairs_list = []
    pair = []

    def __init__(self, state=None, *args, **kwargs):
        super(SirconSpider, self).__init__(*args, **kwargs)
        self.state = state
        alphabet = string.ascii_lowercase
        combinations = list(product(alphabet[:2], repeat=2))
        combinations = [''.join(combination) for combination in combinations]
        for item in combinations:
            for item1 in combinations:
                self.pairs_list.append([item, item1])
        print(self.pairs_list)
        print(len(self.pairs_list))
        self.pair = self.pairs_list.pop()
        # self.pair = ['ma', 'ab']
        print(self.pair)

    headers = {
        'authority': 'www.sircon.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image'
                  '/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    payload = {}

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.sircon.com/ComplianceExpress/Inquiry/consumerInquiry.do?nonSscrb=Y",
            callback=self.parse, headers=self.headers, method='GET', body=str(self.payload))

    def parse(self, response, **kwargs):
        token = response.xpath("//script/text()").re_first("verToken = '(.*)';")
        print(token)
        payload = (f'licenseNumber=&lastName={self.pair[1]}&firstName={self.pair[0]}&city=&addressType=01&'
                   f'licenseType=&qualificationType=&action=search&maxRecords=10&state={self.state}&'
                   f'entityType=IL&addressType=01&fname=&lname=Lincoln&verToken={token}')
        self.headers['cache-control'] = 'max-age=0'
        self.headers['content-type'] = 'application/x-www-form-urlencoded'
        self.headers['origin'] = 'https://www.sircon.com'
        self.headers['referer'] = 'https://www.sircon.com/ComplianceExpress/Inquiry/consumerInquiry.do'

        yield scrapy.Request(url="https://www.sircon.com/ComplianceExpress/Inquiry/consumerInquiry.do", method="POST",
                             headers=self.headers, body=payload, callback=self.data, meta={'token': token})

    def data(self, response):
        records = response.xpath('//tr[contains(@class, "ResultTableTextEvenRow") '
                                 'or contains(@class, "ResultTableTextOddRow")]')
        print(len(records))
        items1 = []
        for record in records:
            item = dict()
            items = record.xpath("./td[@class='ResultTableTextColumn']")
            item['detail_url'] = urljoin("https://www.sircon.com", items[0].xpath("./a/@href").get())
            item['name'] = items[0].xpath("./a/text()").get()
            item['license_number'] = items[1].xpath(".//td[@class= "
                                                    "'ResultTableTextColumn']/text()").getall()[-1].strip()
            item['status'] = items[2].xpath('./text()').get().strip()
            item['producer_number'] = items[3].xpath('./text()').get().strip()
            item['city'] = items[4].xpath('./text()').get().strip()
            # item['state'] = items[5].xpath('./text()').get().strip()
            items1.append(item)
        print(items1)
        request = scrapy.Request(url="https://www.sircon.com/ComplianceExpress/Inquiry/"
                                     "consumerInquiry.do?nonSscrb=Y",
                                 callback=self.again_set_session, headers=self.headers,
                                 method='GET', body=str(self.payload), dont_filter=True, meta={"items": items1})
        request.meta['cookiejar'] = None
        request.cookies = {}
        yield request

    def again_set_session(self, response):
        token = response.xpath("//script/text()").re_first("verToken = '(.*)';")
        print(token)
        payload = (f'licenseNumber=&lastName={self.pair[1]}&firstName={self.pair[0]}&city=&addressType=01&'
                   f'licenseType=&qualificationType=&action=search&maxRecords=10&state={self.state}&'
                   f'entityType=IL&addressType=01&fname=&lname=Lincoln&verToken={token}')
        yield scrapy.Request(url="https://www.sircon.com/ComplianceExpress/Inquiry/consumerInquiry.do", method="POST",
                             headers=self.headers, body=payload,
                             callback=self.again_search_data, meta={'items': response.meta.get('items')},
                             dont_filter=True)

    def again_search_data(self, response):
        items = response.meta.get('items')
        if items:
            item = items.pop()
            print(item)
            yield scrapy.Request(url=item['detail_url'], headers=self.headers,
                                 callback=self.detail_page, method='GET', meta={'item': item, 'items': items})
        else:
            if self.pairs_list:
                self.pair = self.pairs_list.pop()
                print(self.pair)
                request = scrapy.Request(
                    url="https://www.sircon.com/ComplianceExpress/Inquiry/consumerInquiry.do?nonSscrb=Y",
                    callback=self.parse, headers=self.headers, method='GET',
                    body=str(self.payload), dont_filter=True)
                request.meta['cookiejar'] = None
                request.cookies = {}
                yield request

    def detail_page(self, response):
        item = response.meta.get('item')
        tables = response.xpath("//form/table")
        print(len(tables))
        if len(tables) >= 2:
            values = tables[2].xpath('.//tr/td[@valign= "MIDDLE"]/text()').getall()
            if len(values) > 0:
                item['address'] = ' '.join([value.strip() for value in values[0:-1]])
                item['phone'] = values[-1].strip()
            keys = [value.strip() for value in tables[3].xpath('.//tr[@class = '
                                                               '"DataTableLabelRowTextRow"]/td/text()').getall()]
            values = [value.strip() for value in tables[3].xpath('.//tr[@class = '
                                                                 '"DataTableTextEvenRow"]/td/text()').getall()]
            for i in range(0, len(keys)):
                item[keys[i]] = values[i]

        yield item
        print(list(item.keys()))
        request = scrapy.Request(url="https://www.sircon.com/ComplianceExpress/Inquiry/"
                                     "consumerInquiry.do?nonSscrb=Y",
                                 callback=self.again_set_session, headers=self.headers,
                                 method='GET', body=str(self.payload), meta={'items': response.meta.get('items')},
                                 dont_filter=True)
        request.meta['cookiejar'] = None
        request.cookies = {}
        yield request
