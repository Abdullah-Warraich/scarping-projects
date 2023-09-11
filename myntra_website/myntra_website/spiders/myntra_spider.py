import json
from urllib.parse import urljoin
import scrapy


class MyntraSpider(scrapy.Spider):
    headers = {
        'authority': 'www.myntra.com',
        # 'accept-language': 'en-US,en;q=0.9',
        # 'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      # '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    custom_settings = {
        # 'CONCURRENT_REQUESTS': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        # 'CONCURRENT_REQUESTS_PER_IP': 2,
        # 'DOWNLOAD_DELAY': 0.2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': ['productId', 'productName', 'rating', 'ratingCount', 'discount', 'sizes',
                               'brand', 'price', 'gender', 'images', 'Product Details', 'MATERIAL & CARE',
                               'Body or Garment Size', 'Fabric', 'Fabric 2', 'Hemline','Length',
                               'Main Trend', 'Occasion', 'Pattern', 'Print or Pattern Type',
                               'Sleeve Length', "Sleeve Styling", "Stitch", 'Sustainable', 'Wash Care',
                               'Weave Pattern', 'Collar',
                               'SIZE & FIT', 'Body Shape ID', 'Colour Family', 'Design Styling',
                               'Fabric Purity', 'Neck', 'Ornamentation', 'Shape', 'Slit Detail',
                               'Technique', 'Weave Type', 'specifications', 'landingPageUrl'
                               ],
    }
    name = "myntra_spider"
    start_urls = ["https://www.myntra.com/"]

    def parse(self, response):
        men_columns = response.xpath("//div[@class = 'desktop-categoryContainer' and @data-group='men']")
        women_columns = response.xpath("//div[@class = 'desktop-categoryContainer' and @data-group='women']")
        kids_columns = response.xpath("//div[@class = 'desktop-categoryContainer' and @data-group='kids']")

        women_relative_urls = [url for column in women_columns for url in column.xpath(".//li/ul/li/a[@class="
                                                                                       "'desktop-categoryName']"
                                                                                       "/@href").getall()]
        men_relative_urls = [url for column in men_columns for url in column.xpath(".//li/ul/li/a[@class='desktop-"
                                                                                   "categoryName']/@href").getall()]
        kids_relative_urls = [url for column in kids_columns for url in column.xpath(".//li/ul/li/a[@class='desktop-"
                                                                                     "categoryName']/@href").getall()]
        relative_urls = men_relative_urls + women_relative_urls + kids_relative_urls
        print(relative_urls)
        for relative_url in relative_urls:
            yield scrapy.Request(
                urljoin(self.start_urls[0], relative_url),
                headers=self.headers,
                callback=self.records,
            )

    def records(self, response):
        json_data = json.loads(response.xpath('//script/text()').re_first('window.__myx = (.*)'))
        products = json_data.get('searchData', '').get('results', '').get('products', '')
        next_page = response.xpath("//link[@rel = 'next']/@href").get('')
        for product in products:
            item = dict()
            item['productId'] = product.get('productId', '')
            item['productName'] = product.get('productName', '')
            item['rating'] = product.get('rating', '')
            item['ratingCount'] = product.get('ratingCount', '')
            item['discount'] = product.get('discount', '')
            item['sizes'] = product.get('sizes', '')
            item['brand'] = product.get('brand', '')
            item['price'] = product.get('price', '')
            item['gender'] = product.get('gender', '')
            item['images'] = '|'.join([image.get('src', '') for image in product.get('images', '')])
            item['landingPageUrl'] = urljoin(self.start_urls[0], product.get('landingPageUrl', ''))
            yield scrapy.Request(
                urljoin(self.start_urls[0], product.get('landingPageUrl', '')),
                headers=self.headers,
                callback=self.details,
                meta={'item': item}
            )

        if next_page and '?p=2' not in next_page:
            print("next page: ", next_page)
            yield scrapy.Request(
                urljoin(self.start_urls[0], next_page),
                callback=self.records)

    @staticmethod
    def details(response):
        item = response.meta.get('item')
        json_data = json.loads(response.xpath('//script/text()').re_first('window.__myx = (.*)'))
        product_details = json_data.get('pdpData', '').get('productDetails', '')
        for i in product_details:
            item[f"{i.get('title', '')}"] = i.get('description', '').replace('<br>', ',')
        product_attribute = json_data.get('pdpData', '').get('articleAttributes', '')
        item['Body or Garment Size'] = product_attribute.get('Body or Garment Size', '')
        item['Fabric'] = product_attribute.get('Fabric', '')
        item['Fabric 2'] = product_attribute.get('Fabric 2', '')
        item['Hemline'] = product_attribute.get('Hemline', '')
        item['Length'] = product_attribute.get('Length', '')
        item['Main Trend'] = product_attribute.get('Main Trend', '')
        item['Occasion'] = product_attribute.get('Occasion', '')
        item['Pattern'] = product_attribute.get('Pattern', '')
        item['Print or Pattern Type'] = product_attribute.get('Print or Pattern Type', '')
        item['Sleeve Length'] = product_attribute.get('Sleeve Length', '')
        item['Sleeve Styling'] = product_attribute.get('Sleeve Styling', '')
        item['Stitch'] = product_attribute.get('Stitch', '')
        item['Sustainable'] = product_attribute.get('Sustainable', '')
        item['Wash Care'] = product_attribute.get('Wash Care', '')
        item['Weave Pattern'] = product_attribute.get('Weave Pattern', '')
        item['Collar'] = product_attribute.get('Collar', '')

        item['Body Shape ID'] = product_attribute.get('Body Shape ID', '')
        item['Design Styling'] = product_attribute.get('Design Styling', '')
        item['Neck'] = product_attribute.get('Neck', '')
        item['Ornamentation'] = product_attribute.get('Ornamentation', '')
        item['Shape'] = product_attribute.get('Top Shape', '')
        item['Slit Detail'] = product_attribute.get('Slit Detail', '')
        item['Technique'] = product_attribute.get('Technique', '')
        item['Weave Type'] = product_attribute.get('Weave Type', '')
        details = json_data.get('pdpData', '').get('productDetails', '')
        if len(details) == 3:
            item['SIZE & FIT'] = details[2].get('description', '')
        item['specifications'] = str(json_data.get('pdpData', '').get('articleAttributes', '')).strip('{}')
        yield item
