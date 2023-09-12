import urllib.parse
import scrapy


class UhaulSpider(scrapy.Spider):

    def __init__(self, PickupLocation=None, DropoffLocation=None, PickupDate=None, *args, **kwargs):
        super(UhaulSpider, self).__init__(*args, **kwargs)
        self.PickupLocation = PickupLocation
        self.DropoffLocation = DropoffLocation
        self.PickupDate = PickupDate

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
        'FEED_EXPORT_FIELDS': ['truck_name', 'truck_capacity', 'price','Inside dimensions',
                               'Door opening', 'Deck dimensions', 'Loading Ramp', 'image_url'],
    }
    json_data = ("UsedGeocoded=false&PreviouslySharedLocation=false&PreviouslySharedLocationDetail="
                 "&Latitude=0&Longitude=0&ReverseGeoCodeLocation=&PickupLocation=Los+Angeles%2C+"
                 "CA&DropoffLocation=Las+Vegas%2C+NV&PickupDate=09%2F16%2F2023&View=~%2FViews%2"
                 "FHome%2F_EquipmentSearchFormFluid.cshtml&Scenario=TruckOnly&IsActionFrom=False")
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.uhaul.com',
        'Referer': 'https://www.uhaul.com/',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-platform': '"Windows"',
    }
    name = "uhaul_spider"
    start_urls = ["https://www.uhaul.com/"]
    reservation = ("https://www.uhaul.com/Misc/EquipmentSearch/?Area=&scenario="
                   "TruckOnly&isActionForm=False&isAlternateLayout=False&isTowMycar=True")
    trucks = "https://www.uhaul.com/Reservations/RatesTrucks/"

    def parse(self, response):

        pairs = self.json_data.split('&')
        query_params = {}

        for pair in pairs:
            key, value = pair.split('=')
            key = urllib.parse.unquote(key)
            value = urllib.parse.unquote(value)
            query_params[key] = value
        query_params['PickupLocation'] = self.PickupLocation
        query_params['DropoffLocation'] = self.DropoffLocation
        query_params['PickupDate'] = self.PickupDate

        key_value_pairs = []
        query_string = ''
        for key, value in query_params.items():
            key = urllib.parse.quote(key)
            value = urllib.parse.quote(value)
            key_value_pairs.append(f"{key}={value}")
            query_string = '&'.join(key_value_pairs)

        yield scrapy.Request(self.reservation, headers=self.headers, body=query_string,
                             callback=self.start_scraping, method='POST')

    def start_scraping(self, response):
        print(response.body)
        yield scrapy.Request(self.trucks, headers=self.headers,
                             callback=self.trucks_response, method='GET')

    @staticmethod
    def trucks_response(response):
        for data in response.css('li div.grid-padding-x'):
            item = dict()
            item['truck_name'] = data.xpath('.//h3[@class="text-2x"]/text()').get('').strip()
            item['truck_capacity'] = data.xpath(".//dd[@class='text-bold text-xl']/text()").get('').strip()
            details = data.xpath('.//ul[@class="disc hide-for-small-only"]/li/text()').getall()
            cleaned_data_list = [detail.strip() for detail in details if detail.strip()]
            item['price'] = (data.xpath('.//b[@class="block text-3x medium-text-2x text-callout medium-text-base"]'
                                        '/text()').get('').strip())
            item['image_url'] = data.xpath('.//img[@class="margin-y"]/@src').get()
            for detail in cleaned_data_list:
                if 'inside dimensions:' in detail.lower():
                    item['Inside dimensions'] = detail.split(': ')[1:]
                if 'door opening:' in detail.lower():
                    item['Door opening'] = detail.split(': ')[1:]
                if 'height' in detail.lower():
                    item['Deck dimensions'] = ' '.join(detail.split(' ')[1:])
                if 'ramp' in detail.lower() and 'none' not in detail.lower():
                    item['Loading Ramp'] = detail

            yield item
