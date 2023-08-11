from pathlib import Path

import scrapy
from scrapy.http import FormRequest

from ..items import BooksscrapingItem
from urllib.parse import urljoin


class QuotesSpider(scrapy.Spider):
    name = "books"
    base_url = "https://books.toscrape.com/"

    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(self, response):
        details_link = response.xpath("//li[@class='col-xs-6 col-sm-4 col-md-3 col-lg-3']/article/h3/a/@href").getall()
        print(details_link)

        for link in details_link:
            if 'catalogue' in link:
                yield scrapy.Request(url="https://books.toscrape.com/"+link, callback=self.parse_link)
            else:
                yield scrapy.Request(url="https://books.toscrape.com/catalogue/"+link, callback=self.parse_link)

        next_page = response.xpath("//li[@class = 'next']/a/@href").get()
        print("next page is: ", next_page)

        if next_page is not None:
            if 'catalogue' in next_page:
                yield response.follow(urljoin(self.base_url, next_page), callback=self.parse)
            else:
                yield response.follow(urljoin("https://books.toscrape.com/catalogue/", next_page), callback=self.parse)

    def parse_link(self, response):
        item = dict()
        # print(response.xpath("//div[@class = 'item active']/img/@src").get())
        link = response.xpath("//div[@class = 'item active']/img/@src").get()
        name = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()
        price = response.xpath("//div[@class='col-sm-6 product_main']/p[@class ='price_color']/text()").get()
        details = response.xpath("//table/tr/td/text()").getall()
        in_stock_count = details[5].split('(')[1]
        desc = response.xpath("//article/p/text()").get()
        breadcrumb = response.xpath("//ul[@class = 'breadcrumb']/li/a/text()").getall()
        breadcrumb.append(response.xpath("//ul[@class = 'breadcrumb']/li[@class = 'active']/text()").get())
        # print(details)
        item['image_urls'] = [urljoin(self.base_url, link[6:])]
        item['name'] = name
        item['description'] = desc
        item['price'] = price[1:]
        item['item_upc'] = details[0]
        item['in_stock'] = details[5]
        item['in_stock_count'] = in_stock_count[:2]
        item['breadcrumbs'] = '/'.join([n for n in breadcrumb])

        yield item
        # yield BooksscrapingItem(image_urls=urljoin(base_url, link[6:]), name=name)
        # yield {'image_urls': [urljoin(base_url, link[6:])]}



