import scrapy
from scrapy.pipelines.images import ImagesPipeline


# useful for handling different item types with a single interface


class BooksscrapingPipeline(ImagesPipeline):
    print("hi")

    # def get_media_requests(self, item, info):
    #     i = 0
    #     for image_url in item['image_urls']:
    #         i += 1
    #         print(image_url)
    #         yield scrapy.Request(image_url, meta={'i': i})

    def file_path(self, request, response=None, info=None, *, item=None):
        name = item["name"]
        name = name.replace(":", "").replace("?", "").replace("*", "").replace("\\", "").replace(",", "").replace("\"", "")
        return f'/{name}.jpg'

    def item_completed(self, results, item, info):
        # image_paths = [x['path'] for ok, x in results if ok]
        # if not image_paths:
        #     raise scrapy.exceptions.DropItem("Item contains no images")
        # item['image_urls'] = image_paths
        return item
