import json
from copy import deepcopy
from urllib.parse import urlencode
import scrapy
from scrapy.utils.response import open_in_browser
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest


class ZillowSpiderSpider(ScrapingBeeSpider):
    name = "zillow_spider"
    custom_settings = {'ROBOTSTXT_OBEY': False,
                       'RETRY_TIMES': 5,
                       'DOWNLOAD_DELAY': 1,
                       'CONCURRENT_REQUESTS': 1,
                       'FEED_URI': 'output/zillow_spider.xlsx',
                       'FEED_FORMAT': 'xlsx',
                       'FEED_EXPORT_ENCODING': 'utf-8',
                       # 'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
                       'SCRAPINGBEE_API_KEY': 'XF0AXZJVUGDU5Z53S3MI0PEELNE8K2GOKJEAM3N8GJEH7A1MFWVN1TJXPXIP4Z9PFMQRZJ8W3LAJQEAA',
                       'DOWNLOADER_MIDDLEWARES': {'scrapy_scrapingbee.ScrapingBeeMiddleware': 725}
                       }
    headers = {
        'authority': 'www.zillow.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'zguid=24|%24f8149c67-7bd0-4ef3-b108-746c10f6c33d; zgsession=1|9ed24d21-90ca-4d10-9b6b-ad5fa3c88292; _ga=GA1.2.154075965.1694759461; _gid=GA1.2.1889301566.1694759461; zjs_anonymous_id=%22f8149c67-7bd0-4ef3-b108-746c10f6c33d%22; zjs_user_id=null; zg_anonymous_id=%22c4fbd29a-7f2d-4c27-91a2-1a69411bd4dd%22; _gcl_au=1.1.754909016.1694759462; DoubleClickSession=true; pxcts=5d9b234f-5391-11ee-aa84-835a3b460182; _pxvid=5d9b1299-5391-11ee-aa84-7003240f5c52; __pdst=9fbfc546e82c4f359c8d2fff2426eb2a; _fbp=fb.1.1694759470945.1062494261; _pin_unauth=dWlkPVl6VTBZamhqT1RNdE56RTNaaTAwTXpFeUxXRXhaalF0T1dFek5HVTFaR0ZtTkRJMQ; _clck=vxzcfk|2|ff1|0|1353; FSsampler=1584303648; JSESSIONID=66583C1CC76E38BCA5120EF6222DD02D; tfpsi=a0e89d16-7ea6-431e-8021-ab6b11f0d0e2; x-amz-continuous-deployment-state=AYABeG6w1r5i+ErWkjxGTMHdxNoAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADMR5UYc0CDQaBT30+gAwwnRke3FpcApRDjWya7EwBinqa5%2FYg3pb+vIYpV%2Fb8goDaJGSwPyXYQKKsQeeNDftAgAAAAAMAAQAAAAAAAAAAAAAAAAAAEQ6KTKqLNEi8ZLTvb9RkQn%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAwI6fyTVaWPRscGWA5qkQsDutZOd7mhtjPz0h39ZOd7mhtjPz0h3w==; _gat=1; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_cfp=1; _pxff_bsco=1; search=6|1697360638511%7Crect%3D34.267076234205256%2C-117.19449876171876%2C33.663424603955676%2C-119.35331223828126%26rid%3D95984%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26listPriceActive%3D1%26baths%3D3.0-%26beds%3D4-%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%0995984%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09; __gads=ID=c7a3a86198dda95d:T=1694760246:RT=1694768640:S=ALNI_MbVemHp3Ohsvz2EOOm163M6CPFcNg; __gpi=UID=00000ca15bd90df1:T=1694760246:RT=1694768640:S=ALNI_MYSvBqEG0uJfMHB2PTjKdrOqrZF6Q; _hp2_id.1215457233=%7B%22userId%22%3A%227366386339100261%22%2C%22pageviewId%22%3A%222265972612853530%22%2C%22sessionId%22%3A%227803696774092854%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _px3=2070b6e5cf44b5c3affe88030ba6d71a5626f4f66e92a47212c37831ac84f08e:VaylFXsdK6FdXrKuaAG5oF8KYKs6ybhkKcAjJuC2bnYg8uF3jamc2JUI9cKU8vj5avgQ9EMw2jH27/zm/xSmLA==:1000:ZnJ3quocoDDMXVyXi499AoQiB5grv/Q9JgqP2WcYfHICpvzbzMG3kOSAkAWAqVGyhAnnL0t//fkZNmJISICy6UOb4ePunSKCVcPpKyROV/v3n9MSnGdz7vZUGQoZbcUJ2XAGzNr/f6zsVoKBcvoyE2hdgtSEC1nnV8Frqmbw/oUZX1gsKkd6kHgzdLD0EqOTQ3LL4A8jgMjKiLKj4gpj7g==; _hp2_ses_props.1215457233=%7B%22ts%22%3A1694768694517%2C%22d%22%3A%22www.zillow.com%22%2C%22h%22%3A%22%2F%22%7D; _uetsid=75b93b10539111eebca64148bd6f79ac; _uetvid=75b9ace0539111ee8d9e7bef1d45bf8f; _clsk=1rut27l|1694768696567|14|0|h.clarity.ms/collect; AWSALB=ePkECIdVK8bU7e9sv8Hb43Y4EZ5nKK71FLrf/BQp4sJHR7QodV+F9wJXra/JQHAhFjuMWVxqakdopppVOA+sSQOPMQWuYpnwiKuYWvUFl0JCbEytRsl6zR8cOXlE; AWSALBCORS=ePkECIdVK8bU7e9sv8Hb43Y4EZ5nKK71FLrf/BQp4sJHR7QodV+F9wJXra/JQHAhFjuMWVxqakdopppVOA+sSQOPMQWuYpnwiKuYWvUFl0JCbEytRsl6zR8cOXlE',
        'dnt': '1',
        'if-none-match': '"3c69d-z5hA0VpniYIUvZTn6KirNjliE8s"',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    search_data = {"searchQueryState": {"pagination": {'currentPage': 1},
                                        "filterState": {"beds": {"min": 4}, "baths": {"min": 3},
                                                        "sort": {"value": "globalrelevanceex"},
                                                        "fore": {"value": "false"}, "ah": {"value": "true"},
                                                        "auc": {"value": "false"}, "nc": {"value": "false"},
                                                        "fsbo": {"value": "false"},
                                                        "cmsn": {"value": "false"}, "fsba": {"value": "false"},
                                                        "fr": {"value": "false"}, "rs": {"value": "true"}},
                                        "isListVisible": "true"}}

    zip = '90003'
    final_url = 'https://www.zillow.com/homes/{}_rb/?{}'.format(zip, urlencode(search_data))

    def start_requests(self):
        yield ScrapingBeeRequest(url=self.final_url, headers=self.headers, meta={'current_page': 1})

    def parse(self, response, **kwargs):
        open_in_browser(response)
        json_data = json.loads(response.css("#_NEXT_DATA_::text").get(''))
        homes_list = json_data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get(
            'searchResults', {}).get('listResults', [])
        item = dict()
        for home in homes_list:
            item['address'] = home.get('address', '')
            item['addressCity'] = home.get('addressCity', '')
            item['addressState'] = home.get('addressState', '')
            item['addressStreet'] = home.get('addressStreet', '')
            item['addressZipcode'] = home.get('addressZipcode', '')
            item['area'] = home.get('area', '')
            item['baths'] = home.get('baths', '')
            item['beds'] = home.get('beds', '')
            item['brokerName'] = home.get('brokerName', '')
            item['detailUrl'] = home.get('detailUrl', '')
            item['imgURL'] = home.get('imgSrc', '')
            item['statusType'] = home.get('statusType', '')
            item['statusText'] = home.get('statusText', '')
            item['price'] = home.get('price', '')
            item['unformattedPrice'] = home.get('unformattedPrice', '')
            yield item
        current_page = response.meta['current_page']
        total_page = int(json_data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).
                         get('searchList', {}).get('totalPages', ''))
        # print(type(total_page), total_page)
        # print(type(current_page), current_page)
        # if current_page < total_page:
        #     search_data_copy = deepcopy(self.search_data)
        #     search_data_copy['searchQueryState']['pagination']['currentPage'] = current_page + 1
        #     print(search_data_copy)
        #     url = 'https://www.zillow.com/homes/{}_rb/?{}'.format(self.zip, urlencode(search_data_copy))
        #     yield ScrapingBeeRequest(url=url, headers=self.headers, callback=self.parse,
        #                           meta={'current_page': current_page + 1})
