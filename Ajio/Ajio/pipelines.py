import time

import scrapy
from scrapy.pipelines.images import ImagesPipeline


class AjioPipeline(ImagesPipeline):
    print("hi")

    def custom_image_name(request, response=None, info=None):
        import time
        timestamp = int(time.time() * 1000)  # Use milliseconds for uniqueness
        image_extension = request.url.split('.')[-1]
        image_name = '.'.join(request.url.split('/')[-2:])
        image_name = f"{image_name}.{image_extension}"
        return image_name

    def item_completed(self, results, item, info):
        item['image_path'] = [x['path']+": "+x['url'] for ok, x in results if ok]
        # if not image_path:
        #     raise scrapy.exceptions.DropItem('Image not exist')
        # item['Downloaded image'] = self.store.basedir[1:]+'\\'+'|'.join(image_path[1:])

        return item
