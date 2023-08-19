import json
from urllib.parse import urljoin
import scrapy


class MyntraSpider(scrapy.Spider):
    name = "myntra_spider"
    start_urls = ["https://www.myntra.com/"]

    def parse(self, response):
        columns = response.xpath("//div[@class = 'desktop-categoryContainer' and @data-group='men']")
        relative_urls = [url for column in columns for url in column.xpath(".//li/ul/li/a[@class='desktop-"
                                                                           "categoryName']/@href").getall()]
        print(relative_urls)
        for relative_url in relative_urls:
            yield scrapy.Request(
                urljoin(self.start_urls[0], relative_url),
                callback=self.records,
            )

    def records(self, response):
        json_data = json.loads(response.xpath('//script/text()').re_first('window.__myx = (.*)'))
        products = json_data['searchData']['results']['products']
        next_page = response.xpath("//link[@rel = 'next']/@href").get()
        for product in products:
            item = dict()
            item['productId'] = product.get('productId')
            item['productName'] = product.get('productName')
            item['rating'] = product.get('rating')
            item['ratingCount'] = product.get('ratingCount')
            item['discount'] = product.get('discount')
            item['sizes'] = product.get('sizes')
            item['brand'] = product.get('brand')
            item['price'] = product.get('price')
            item['gender'] = product.get('gender')
            item['images'] = '|'.join([image.get('src') for image in product.get('images')])
            item['landingPageUrl'] = product.get('landingPageUrl')
            yield scrapy.Request(
                urljoin(self.start_urls[0], product.get('landingPageUrl')),
                callback=self.details,
                meta={'item': item}
            )

        if next_page is not None and '?p=11' not in next_page:
            print("next page: ", next_page)
            yield scrapy.Request(
                urljoin(self.start_urls[0], next_page),
                callback=self.records)

    def details(self, response):
        item = response.meta.get('item')
        json_data = json.loads(response.xpath('//script/text()').re_first('window.__myx = (.*)'))
        product_details = json_data.get('pdpData').get('productDetails')
        for i in product_details:
            item[f"{i.get('title')}"] = i.get('description').replace('<br>', ',')
        product_attribute = json_data.get('pdpData').get('articleAttributes')
        item['Body or Garment Size'] = product_attribute.get('Body or Garment Size')
        item['Fabric'] = product_attribute.get('Fabric')
        item['Fabric 2'] = product_attribute.get('Fabric 2')
        item['Hemline'] = product_attribute.get('Hemline')
        item['Length'] = product_attribute.get('Length')
        item['Main Trend'] = product_attribute.get('Main Trend')
        item['Occasion'] = product_attribute.get('Occasion')
        item['Pattern'] = product_attribute.get('Pattern')
        item['Print or Pattern Type'] = product_attribute.get('Print or Pattern Type')
        item['Sleeve Length'] = product_attribute.get('Sleeve Length')
        item['Sleeve Styling'] = product_attribute.get('Sleeve Styling')
        item['Stitch'] = product_attribute.get('Stitch')
        item['Sustainable'] = product_attribute.get('Sustainable')
        item['Wash Care'] = product_attribute.get('Wash Care')
        item['Weave Pattern'] = product_attribute.get('Weave Pattern')
        item['Collar'] = product_attribute.get('Collar')

        yield item

