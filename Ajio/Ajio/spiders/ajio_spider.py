import json
from copy import deepcopy
from urllib.parse import urljoin
import scrapy


class AjioSpider(scrapy.Spider):
    headers = {
        'Referer': 'https://www.ajio.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    custom_settings = {
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 3.0,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'CUNCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1,
        'REDIRECT_ENABLED': False,
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
        'ITEM_PIPELINES': {
            "Ajio.pipelines.AjioPipeline": 1,
        },
        'IMAGES_STORE': r".\images",
    }

    name = "ajio_spider"
    start_urls = ["https://www.ajio.com/"]

    def parse(self, response, **kwargs):
        json_data = json.loads(response.xpath('//script/text()').re_first(r'{"wishlist":{},'
                                                                          r'"navigation":.*"location":{}}'))
        main_categories = json_data.get('navigation',
                                        {}).get('data', {}).get('childDetails',
                                                                [{}])[0].get('childDetails',
                                                                             [{}])[0].get('childDetails', [])
        main_categories_links = [cat.get('url', '') for cat in main_categories]
        print(main_categories_links)
        main_categories_links.remove('/shop/international-brands')
        main_categories_links.remove('')
        for main_categories_link in main_categories_links:
            yield scrapy.Request(urljoin(self.start_urls[0], main_categories_link), callback=self.records)

    def records(self, response):
        json_data = json.loads(response.xpath('//script/text()').re_first(r'{"wishlist":{},'
                                                                          r'"navigation":.*"location":{.*}}'))
        ids = json_data.get('grid', {}).get('results', {})
        entities = json_data.get('grid', {}).get('entities', {})
        for id1 in ids:
            product = entities.get(f'{id1}', {})
            item = dict()
            item['code'] = product.get('code', '')
            item['couponStatus'] = product.get('couponStatus', '')
            item['brandName'] = product.get('fnlColorVariantData', {}).get('brandName', '')
            item['discountPercent'] = product.get('discountPercent', '')
            item['currency'] = product.get('price', {}).get('currencyIso', '')
            item['price'] = product.get('price', {}).get('formattedValue', '')
            item['was_priced'] = product.get('wasPriceData', {}).get('formattedValue', '')
            detail_url = urljoin(self.start_urls[0], product.get('url', ''))
            yield scrapy.Request(detail_url, callback=self.details,
                                 meta={'item': item, 'already_requested_urls': list(detail_url)})

        header = self.headers
        header['Referer'] = urljoin('https://www.ajio.com', json_data.get('request', {}).get('pathname', ''))
        header['accept'] = 'application/json'
        curated_id = json_data.get('request', {}).get('query', {}).get('curatedid', '')
        pagination_url = ("https://www.ajio.com/api/category/83?currentPage=1&pageSize=45&"
                          "format=json&query=%3Arelevance&sortBy=relevance&curated=true&"
                          "curatedid={}&gridColumns=3&facets=&advfilter=true"
                          "&platform=Desktop&showAdsOnNextPage=true&is_ads_enable_plp=true"
                          "&displayRatings=true").format(curated_id)
        yield scrapy.Request(pagination_url, headers=header, callback=self.pagination,
                             meta={'curatedid': curated_id, 'path': json_data.get('request', '').get('pathname', '')})

    def pagination(self, response):
        data = json.loads(response.body)
        products = data.get('products', '')
        for product in products:
            item = dict()
            item['code'] = product.get('code', '')
            item['couponStatus'] = product.get('couponStatus', '')
            item['brandName'] = product.get('fnlColorVariantData', '').get('brandName', '')
            item['color_group'] = product.get('fnlColorVariantData', '').get('colorGroup', '')
            item['name'] = product.get('name', '')
            images = ' | '.join([item.get('url', '') for item in product.get('images', [])])
            images1 = ' | '.join([item.get('images', [{}])[0].get('url', '')
                                  for item in product.get('extraImages', [])])
            item['images'] = images + ' | ' + images1
            item['discountPercent'] = product.get('discountPercent', '')
            item['currency'] = product.get('price', {}).get('currencyIso', '')
            item['price'] = product.get('price', {}).get('formattedValue', '')
            item['was_priced'] = product.get('wasPriceData', {}).get('formattedValue', '')
            item['detail_url'] = urljoin(self.start_urls[0], product.get('url', ''))
            yield scrapy.Request(item['detail_url'], callback=self.details,
                                 meta={'item': item, 'already_requested_urls': list(item['detail_url'])})
        current = data.get('pagination', {}).get('currentPage', '')
        if current <= data.get('pagination', {}).get('totalPages', ''):
            curated_id = response.meta.get('curatedid')
            header = self.headers
            header['Referer'] = urljoin('https://www.ajio.com', response.meta.get('path'))
            header['accept'] = 'application/json'
            pagination_url = ("https://www.ajio.com/api/category/83?currentPage={}&pageSize=45&"
                              "format=json&query=%3Arelevance&sortBy=relevance&curated=true&"
                              "curatedid={}&gridColumns=3&facets=&advfilter=true"
                              "&platform=Desktop&showAdsOnNextPage=true&is_ads_enable_plp=true"
                              "&displayRatings=true").format((current+1), curated_id)
            yield scrapy.Request(pagination_url, headers=header, callback=self.pagination,
                                 meta={'curatedid': curated_id, 'path': response.meta.get('path')})

    def details(self, response):
        item = deepcopy(response.meta.get('item'))
        already_processed_urls = deepcopy(response.meta.get('already_requested_urls'))
        json_data = json.loads(response.xpath('//script/text()').re_first(r'{"wishlist":{},"navigation.*"'
                                                                          r'location":{.*}}'))
        variants = json_data.get('product', {}).get('productDetails', {}).get('baseOptions',
                                                                              [{}])[0].get('options', [{}])
        item['color_group'] = json_data.get('product', {}).get('productDetails',
                                                               {}).get('request', '').get('optionCode')
        print(item['color_group'])
        item['main_image_urls'] = json_data.get('product',
                                                     {}).get('productDetails', {}).get('images', [])[0].get('url', '')
        print(item['main_image_urls'])
        item['Name'] = json_data.get('product', {}).get('productDetails', {}).get('name', '')
        product_details = json_data.get('product', {}).get('productDetails', {}).get('featureData', [])
        details = []
        for product_detail in product_details:
            details.append(': '.join([product_detail.get('name', ''),
                                     product_detail.get('featureValues', {})[0].get('value', '')]))
        item['product_details'] = '|'.join(details)
        details = json_data.get('product', {}).get('productDetails',
                                                   {}).get('variantOptions',
                                                           [{}])[0].get('mandatoryInfo', [{}])[0]
        mandatory_details = json_data.get('product', {}).get('productDetails', {}).get('mandatoryInfo', [])
        mandatory_info = [':'.join([item.get('key', ''), item.get('title', '')]) for item in mandatory_details]
        mandatory_info.append(':'.join([details.get('key', ''), details.get('title', '')]))
        item['Mandatory_info'] = '|'.join(mandatory_info)

        variants_links = [variant.get('url', '') for variant in variants]
        images_dict = json_data.get('product', {}).get('productDetails', {}).get('images', [])
        # item['images'] = '|'.join([image.get('url', '') for image in images_dict])
        item['image_urls'] = [image.get('url', '') for image in images_dict]
        # item['image_urls'] = [images_dict[0].get('url')]
        item['Detail_url'] = urljoin('https://www.ajio.com',
                                     json_data.get('product', {}).get('productDetails', {}).get('url', ''))
        yield item

        requested_urls = already_processed_urls
        for variants_link in variants_links:
            if urljoin('https://www.ajio.com', variants_link) not in already_processed_urls:
                requested_urls.append([urljoin('https://www.ajio.com', vl) for vl in variants_links])
                yield scrapy.Request(urljoin('https://www.ajio.com', variants_link),
                                     callback=self.details, meta={'item': response.meta.get('item'),
                                                                  'already_requested_urls':
                                                                      requested_urls})
