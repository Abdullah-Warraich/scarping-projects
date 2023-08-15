import scrapy


class QuotesSpider(scrapy.Spider):
    name = "autoscrap"
    base_url = "https://production-proxy.autolist.com/api/v2/search?include_total_price_change=true" \
               "&include_time_on_market=true&include_relative_price_difference=true&latitude=32.5777" \
               "&limit=20&longitude=74.0838&make={}&model={}&radius=100&zip=47580&page={}"
    page = dict()
    count = 0
    make = ''
    model = ''
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.autolist.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.autolist.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def __init__(self, make=None, model=None, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.make = make
        self.models = model.split(',')
        print(self.make)
        print(self.models)

    def start_requests(self):
        url = "https://www.autolist.com/api/lookup/makes"

        headers_for_makes = {
            'authority': 'www.autolist.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'cookie': '_gcl_au=1.1.1531406104.1691749956; _fbp=fb.1.1691749957179.1875170450; '
                      '_pbjs_userid_consent_data=3524755945110770; _pubcid=179c0b0f-bb6f-4099-bbb8-20845a4a514b; '
                      'panoramaId_expiry=1692354789836; _cc_id=2e78a25ca80371cc949522a5f770806d; '
                      'panoramaId=b6efc74d0ab5e61dec00ff5eb36d16d53938194d4bc997e1c9a087b07b10b92d; '
                      'pbjs-unifiedid=%7B%22TDID%22%3A%22e279e608-78c3-459b-9068-7b5ebddedc87%22%2C%22TDID_'
                      'LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222023-07-11T10%3A33%3A10%22%7D; '
                      'ec=eyJlZGdlVXNlckFnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLa'
                      'XQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNS4wLjAuMCBTYWZhcmkvNTM3LjM2In0=; '
                      'client_guid_timestamp=0e56f5f1-d455-43da-85e2-0445abef03e8.1691749954507; '
                      '_gid=GA1.2.687545938.1692035649; _sp_ses.8ca5=*; '
                      '__gads=ID=87ce7a491e947a18:T=1691749959:RT=1692097652:S=ALNI_Ma5RpJHnu-aoFj-MIGSuhP4HuS1dQ; '
                      '__gpi=UID=00000c7c3d264c63:T=1691749959:RT=1692097652:S=ALNI_MaZALWIOy9NNCtNrXBwJEsCDz2OOg; '
                      '_uetsid=91ac8f303acb11eea80eadcf194e901e; _uetvid=62ea5870383211eebae08fdff8739550; '
                      '_ga_KKZ1EQJKEV=GS1.1.1692090122.12.1.1692097664.0.0.0; _ga=GA1.1.1353825984.1691749955; '
                      'cto_bundle=tTaCC185Rjc1QkZnTWZ0bVFiN2taYTRxbVJ6UktDTkpwRVlNTmhXYXFJNXhtYyUyRmRNb0duY0YzcHcyd'
                      'EFxTnZtNUNIVjlsNXMzNU10QVBMRXZpazJEcDhPbyUyQjNvTnQwZ2x6Y1UxS0prdlo3UnliVUFYOHRRUkZ0c0JWd2xUZ29'
                      'qQTJ3UHE1bU5QVE1jZ0dHZ0c1N3BtTHd1OVJ3JTNEJTNE; cto_bidid=UYScwV80eTJXMjgyS3ZBMU5pbUlPYVNsJTJGNGM'
                      '1QjlFdHVxTUhPbWwxZTVFTGFwZUpzTWhWZTBtUG85TDI4WHlRYjYweFFUV0pFb0U0Qk1OWEklMkJ5SHNnb25nM3ZMNiUyQl'
                      'ZsRDUlMkJoN3FEZXZLTGo5ZTRjJTNE; _sp_id.8ca5=ff7ebb9d-31af-4bbc-a54e-ba9cddc59b0f.1691749955.12'
                      '.1692098907.1692087239.1da90962-1359-42e8-8a3c-d5ccd79cc03f',
            'pragma': 'no-cache',
            'referer': 'https://www.autolist.com/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

        yield scrapy.Request(
            url,
            headers=headers_for_makes,
            callback=self.model_requests
        )

    def model_requests(self, response):
        data = response.json()
        mod = self.models
        self.models = []
        for make in data:
            if make['name'] == self.make:
                for model in make['models']:
                    if model['name'] in mod:
                        self.models.append(model['name'])

        print(self.models)

        for model in self.models:
            self.page[f'{model}'] = 1
            url = self.base_url.format(self.make, model, str(self.page[f'{model}']))

            yield scrapy.Request(
                url,
                method='GET',
                headers=self.headers,
                callback=self.parse
            )

    def parse(self, response):
        data = response.json()
        if data['hits_count'] != 0:
            self.count += data['hits_count']
            print(self.count)
            records = data['records']
            self.page[f"{records[0]['model_name']}"] += 1
            for index, record in enumerate(records):
                item = dict()
                item['make_and_model'] = record['make_and_model']
                item['mileage'] = record['mileage']
                item['phone'] = record['phone']
                item['price'] = record['price']
                item['city'] = record['city']
                item['fuel_type'] = record['fuel_type']
                item['body_type'] = record['body_type']
                item['city_mpg'] = record['city_mpg']
                item['combined_mpg'] = record['combined_mpg']
                item['condition'] = record['condition']
                item['created_at'] = record['created_at']
                item['dealer_name'] = record['dealer_name']
                item['distance_from_origin'] = record['distance_from_origin']
                item['door_count'] = record['door_count']
                item['driveline'] = record['driveline']
                item['hwy_mpg'] = record['hwy_mpg']
                item['lat'] = record['lat']
                item['lon'] = record['lon']
                item['normalized_color_exterior'] = record['normalized_color_exterior']
                item['photo_urls'] = ', '.join(record['photo_urls'])
                item['provider_id'] = record['provider_id']
                item['provider_name'] = record['provider_name']
                item['transmission'] = record['transmission']
                item['warranty'] = record['warranty']
                item['year'] = record['year']

                yield item

            yield scrapy.Request(
                self.base_url.format(self.make, record['model_name'], str(self.page[f"{record['model_name']}"])),
                method='GET',
                headers=self.headers,
                callback=self.parse
            )
