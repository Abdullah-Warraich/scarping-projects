from pathlib import Path

import scrapy
from scrapy.http import FormRequest

from ..items import TutorialItem
from urllib.parse import urljoin


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    start_urls = [
        "https://quotes.toscrape.com/login"
    ]
    # def start_requests(self):
    #     urls = [
    #         "https://quotes.toscrape.com/page/1/",
    #         "https://quotes.toscrape.com/page/2/",
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        token = response.xpath("//form/input/@value").get()
        print(token)
        return FormRequest.from_response(response, formdata={
            'csrf_token': token,
            'username': 'ali',
            'password': 'ali01'
        }, callback=self.start_scraping)

    def start_scraping(self, response):
        items = TutorialItem()
        allrecords = response.xpath("//div[@class = 'quote']")
        for quote1 in allrecords:
            text = quote1.xpath(".//span[@class = 'text']/text()").get()
            author = quote1.xpath(".//span/small[@class = 'author' ]/text()").get()
            author_link = quote1.xpath(".//span/a/@href").get()
            tags = quote1.xpath(".//div[@class = 'tags']/a/text()").getall()
            text = text.replace('“', '')
            items['text'] = text
            items['author'] = author
            items['author_link'] = urljoin("https://quotes.toscrape.com", author_link)
            items['tags'] = tags

            yield items

        next_page = response.xpath("//li[@class = 'next']/a/@href").get()
        print(next_page)
        if next_page is not None:
            yield response.follow(next_page, callback=self.start_scraping)

