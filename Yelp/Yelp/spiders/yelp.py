import json
from urllib.parse import urljoin
import scrapy


class YelpSpider(scrapy.Spider):
    name = "yelp_spider"
    custom_settings = {'ROBOTSTXT_OBEY': False,
                       'RETRY_TIMES': 5,
                       'DOWNLOAD_DELAY': 1,
                       'CONCURRENT_REQUESTS': 1,
                       'FEEDS': {
                           'output1.csv': {
                               'format': 'csv',
                               'overwrite': True,  # This will overwrite the file if it already exists
                           },
                       },
                       }

    url = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=San%20Francisco%2C%20CA"

    payload = {}
    headers = {
        'authority': 'www.yelp.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                  'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.yelp.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse)

    def parse(self, response, **kwargs):
        json_data = json.loads(response.xpath('//script/text()').re_first(r'<!--(.*)-->')
                               ).get('legacyProps', {})
        records = json_data.get('searchAppProps', {}).get('searchPageProps',
                                                          {}).get('mainContentComponentsListProps')
        records_cleaned = []
        for record in records:
            if (record.get('searchResultBusiness', {}) and
                    record.get('searchResultBusiness', {}).get('isAd', True) is False):
                records_cleaned.append(record.get('searchResultBusiness', {}))

        for record in records_cleaned:
            item = dict()
            item['name'] = record.get('name', '')
            item['phone'] = record.get('phone', '')
            item['money'] = record.get('priceRange', '')
            item['rating'] = record.get('rating', '')
            item['reviewCount'] = record.get('reviewCount', '')
            item['detail_url'] = urljoin('https://www.yelp.com/', record.get('businessUrl', ''))

            yield scrapy.Request(url=item['detail_url'],
                                 headers=self.headers, callback=self.details, meta={'item': item})

        page_meta = json_data.get('headerProps', {}).get('pageMetaTagsProps')
        next_page_url = page_meta.get('nextPageUrl', '')
        print(next_page_url)

        if next_page_url is not None:
            yield scrapy.Request(url=next_page_url, headers=self.headers, callback=self.parse)

    def details(self, response):
        item = response.meta.get('item')
        item['business_website'] = response.xpath('//div/div[1]/p[2]/a/text()').get()
        item['popular_dishes'] = ', '.join(response.xpath('//p[@class = " css-nyjpex"]/text()').getall())

        item['address'] = response.xpath('//p[@class = " css-qyp8bo"]/text()').get()
        item['claimed'] = response.xpath('//span/div/span/text()').getall()
        if len(item['claimed']) == 2:
            item['claimed'] = item['claimed'][1]
        else:
            item['claimed'] = []
        item['type'] = ''.join(response.xpath('//span[@class=" css-1xfc281"]/span'
                                              '[@class=" css-1fdy0l5"]//text()').getall())
        item['business_highlights'] = ','.join(response.xpath('//span[@class=" css-1p9ibgf"]/text()').getall())
        data = json.loads(response.xpath('//script/text()').re_first(r'<!--({"locale".*})-->'))
        original_request_id = data.get('legacyProps', {}).get('bizDetailsProps', {}).get('uniqueRequestId', '')
        biz_id = data.get('legacyProps', {}).get('bizDetailsProps',
                                                 {}).get('bizDetailsVendorProps',
                                                         {}).get('adrollTrackingProps',
                                                                 {}).get('customData', {}).get('biz_id', '')
        print(original_request_id)
        url = (f"https://www.yelp.com/biz/{biz_id}/"
               f"props?osq=Restaurants&original_request_id={original_request_id}")
        yield scrapy.Request(url, headers=self.headers, callback=self.about_business, meta={'item': item})

    def about_business(self, response):
        item = response.meta.get('item')
        data = json.loads(response.body)
        data = data.get('bizDetailsPageProps',
                        {}).get('fromTheBusinessProps',
                                {})
        speciality = ''
        historyText = ''
        businessOwnerBio = ''
        item['business_owner'] = ''
        if data:
            data = data.get('fromTheBusinessContentProps', {})
            speciality = data.get('specialtiesText', '')
            historyText = data.get('historyText', '')
            businessOwnerBio = data.get('businessOwnerBio', '')
            if businessOwnerBio:
                item['business_owner'] = data.get('businessOwner', {}).get('markupDisplayName', '')

        item['about_business'] = ('speciality:\n'+str(speciality)+'\n\n'+'historyText:\n' +
                                  str(historyText)+'\n\n'+'businessOwnerBio:\n'+str(businessOwnerBio))
        yield item
        # print(speciality)
