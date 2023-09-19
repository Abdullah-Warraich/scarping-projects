import json
import urllib.parse
from copy import deepcopy
from urllib.parse import urljoin
import csv
import scrapy
import urllib.parse


class ZillowSpider(scrapy.Spider):
    custom_settings = {
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 3.0,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'CUNCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0.5,
        'REDIRECT_ENABLED': False,
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
        'FEED_EXPORT_FIELDS': ['zpid', 'detail_url', 'statusType', 'statusText', 'countryCurrency', 'price', 'address',
                               'addressStreet', 'addressCity', 'addressState', 'addressZipcode', 'beds', 'baths',
                               'area', 'latitude', 'longitude', 'brokerName', 'ImageLink', 'yearBuilt', 'nearbyCities',
                               'nearbyHomes', 'nearbyZipcodes', 'description', 'homeInsights', 'originalPhotos',
                               'atGlanceFacts', 'cooling', 'heating', 'flooring', 'interiorFeatures', 'parkingFeatures',
                               'sewer', 'constructionMaterials', 'exteriorFeatures', 'foundationDetails', 'appliances',
                               'propertySubType', 'mlsName', 'agentName', 'agentEmail', 'agentPhoneNumber',
                               'listingOffices', 'listingAgents', 'schools', 'priceHistory', 'taxHistory',
                               'associations', 'associationFeeIncludes']

        # 'ITEM_PIPELINES': {
        #     "Ajio.pipelines.AjioPipeline": 1,
        # },
        # 'IMAGES_STORE': r"C:\Users\PMLS\Music\Projects\Ajio\images",
    }
    main_url = "https://www.zillow.com/homes/"

    headers = {
        'authority': 'www.zillow.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    name = "zillow_spider"

    def start_requests(self):
        with open(r"C:\Users\PMLS\Music\Projects\Zillow\input.csv", 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                url = ("https://www.zillowstatic.com/autocomplete/v3/suggestions?"
                       f"userLat=39.34966&userLon=-76.28673&clientId=homepage-render&q={urllib.parse.quote(row[0])}")
                yield scrapy.Request(url=url, headers=self.headers, callback=self.__parse)

    def __parse(self, response):
        results = json.loads(response.body).get('results', [{}])
        yield scrapy.Request(url=urljoin(self.main_url,
                                         (str(results[0].get('display', '')) + '_rb/').replace(' ', '-')),
                             headers=self.headers, callback=self._parse,
                             meta={'query': results[0].get('display', ''),
                                   'regionId': results[0].get('metaData', {}).get('regionId', '')})

    def _parse(self, response, **kwargs):
        query = response.meta.get('query')
        regionId = response.meta.get('regionId')
        mapBounds = json.loads(response.xpath('//script//text()').re_first(r'{"west":.*,"north":.*}'))
        url = ("https://www.zillow.com/search/GetSearchPageState.htm?"
               f"searchQueryState=%7B%22usersSearchTerm%22%3A%22{urllib.parse.quote(query)}%22%2C%22mapBounds"
               f"%22%3A%7B%22west%22%3A{mapBounds['west']}%2C%22east%22%3A{mapBounds['east']}%2C%22"
               f"south%22%3A{mapBounds['south']}%2C%22north%22%3A{mapBounds['north']}%7D%2C%22mapZoom"
               f"%22%3A6%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A{regionId}%2C%22regionType%"
               "22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22isAllHomes%"
               "22%3A%7B%22value%22%3Atrue%7D%2C%22sortSelection%22%3A%7B%22value%22%3A%22globalrelevanceex"
               "%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22pagination%22%3A%7B%22currentPage%22%3A1%7D%7D"
               "&wants={%22cat1%22:[%22listResults%22,%22mapResults%22],%22cat2%22:[%22total%22]}&requestId=20")
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,
                             meta={'data': {'query': urllib.parse.quote(query),
                                            'mapBounds': mapBounds, 'regionId': regionId, 'currPage': 1}})

    def parse(self, response, **kwargs):
        data = deepcopy(response.meta.get('data'))
        mapBounds = data.get('mapBounds', {})
        results = deepcopy(json.loads(response.body).get('cat1', {}).get('searchResults', {}).get('listResults', [{}]))
        print(len(results))
        for result in results:
            item = dict()
            item['zpid'] = int(result.get('zpid', 0))
            item['detail_url'] = urljoin('https://www.zillow.com', result.get('detailUrl', ''))
            item['statusType'] = result.get('statusType', '')
            item['statusText'] = result.get('statusText', '')
            item['countryCurrency'] = result.get('countryCurrency', '')
            item['price'] = result.get('unformattedPrice', '')
            item['address'] = result.get('address', '')
            item['addressStreet'] = result.get('addressStreet', '')
            item['addressCity'] = result.get('addressCity', '')
            item['addressState'] = result.get('addressState', '')
            item['addressZipcode'] = result.get('addressZipcode', '')
            item['beds'] = result.get('beds', '')
            item['baths'] = result.get('baths', '')
            item['area'] = result.get('area', '')
            item['latitude'] = result.get('latLong', {}).get('latitude', '')
            item['longitude'] = result.get('latLong', {}).get('longitude', '')
            item['area'] = result.get('area', '')

            link = ('https://www.zillow.com/graphql/?extensions=%7B%22persistedQuery%22%3A%7B%'
                    '22version%22%3A1%2C%22sha256Hash%22%3A%2276c0097009e76a4f99611218abd569ae2dd65ac1'
                    '290b4cd95bcfe040ff9b694b%22%7D%7D&')
            variable = dict({"zpid": item['zpid'], "platform": "DESKTOP_WEB", "formType": "OPAQUE",
                             "contactFormRenderParameter": {"zpid": item['zpid'],
                                                            "platform":"desktop", "isDoubleScroll": True},
                             "skipCFRD": False})
            variable = ((urllib.parse.quote(str(variable).replace(' ', '')).
                         replace('%27', '%22')).replace('True', 'true').
                        replace('False', 'false'))
            yield scrapy.Request(url=link + 'variables=' + variable,
                                 headers=self.headers, callback=self.detail_info, meta={'item': item})

        data['currPage'] += 1
        url = ("https://www.zillow.com/search/GetSearchPageState.htm?"
               f"searchQueryState=%7B%22usersSearchTerm%22%3A%22{data['query']}%22%2C%22mapBounds"
               f"%22%3A%7B%22west%22%3A{mapBounds['west']}%2C%22east%22%3A{mapBounds['east']}%2C%22"
               f"south%22%3A{mapBounds['south']}%2C%22north%22%3A{mapBounds['north']}%7D%2C%22mapZoom"
               f"%22%3A6%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A{data['regionId']}%2C%22regionType%"
               "22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22isAllHomes%"
               "22%3A%7B%22value%22%3Atrue%7D%2C%22sortSelection%22%3A%7B%22value%22%3A%22globalrelevanceex"
               f"%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22pagination%22%3A%7B%22currentPage%22%3A{data['currPage']}"
               "%7D%7D&wants={%22cat1%22:[%22listResults%22,%22mapResults%22],%22cat2%22:[%22total%22]}&requestId=20")
        if data['currPage'] <= json.loads(response.body).get('cat1', {}).get('searchList', {}).get('totalPages', 0):
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse,
                                 meta={'data': {'query': data['query'],
                                                'mapBounds': mapBounds, 'regionId': data['regionId'],
                                                'currPage': data['currPage']}})

    def detail_info(self, response):
        item = response.meta.get('item')
        details = json.loads(response.body).get('data', {}).get('property', {})
        if True:
            item['brokerName'] = details.get('brokerageName', '')
            item['ImageLink'] = details.get('hiResImageLink', '')
            item['yearBuilt'] = details.get('yearBuilt', '')
            item['nearbyCities'] = ','.join([city.get('name') for city in details.get('nearbyCities', [{}])])
            item['nearbyHomes'] = '|'.join([('zpid: ' + str(home.get('zpid', '')) +
                                             ', price: ' + str(home.get('price', '')) +
                                             ', beds: ' + str(home.get('bedrooms', '')) +
                                             ', baths: ' + str(home.get('bathrooms', '')) +
                                             ', currency: ' + str(home.get('currency', '')) +
                                             ', livingArea: ' + str(home.get('livingArea', '')) +
                                             ', livingAreaUnits: ' + str(home.get('livingAreaUnits', '')) +
                                             ', lotSize: ' + str(home.get('lotSize', '')) +
                                             ', address: ' + str(home.get('address', {}).get('streetAddress', ''))
                                             ) for home in details.get('nearbyHomes', [{}])])
            item['nearbyZipcodes'] = '|'.join([zipcode.get('name', '')
                                               for zipcode in details.get('nearbyZipcodes', [{}])])
            item['description'] = details.get('description', '')
            item['homeInsights'] = details.get('homeInsights', [{}])
            if item['homeInsights']:
                item['homeInsights'] = ', '.join(item['homeInsights'][0].get('insights', [{}])[0].get('phrases', []))
            item['originalPhotos'] = [photo.get('mixedSources', {})
                                      for photo in details.get('originalPhotos', [])]
            # item['originalPhotos'] = ','.join([','.join([photo1.get('url', '')
            #                                              for photo1 in photo.get('jpeg', [])]) for photo in
            #                                    item['originalPhotos']])
            item['originalPhotos'] = [photo.get('jpeg', [{}])[0].get('url', '') for photo in item['originalPhotos']]
            atAGlanceFacts = details.get('resoFacts', {}).get('atAGlanceFacts', [{}])
            item['atGlanceFacts'] = ', '.join([fact.get('factLabel', '') + ': ' + str(fact.get('factValue', ''))
                                               for fact in atAGlanceFacts] if atAGlanceFacts else [])
            reso_fact = details.get('resoFacts', {})
            item['cooling'] = ', '.join(reso_fact.get('cooling', [])) if reso_fact.get('cooling', []) else ''
            item['heating'] = ', '.join(reso_fact.get('heating', [])) if reso_fact.get('heating', []) else ''
            item['flooring'] = ', '.join(reso_fact.get('flooring', [])) if reso_fact.get('flooring', []) else ''
            item['interiorFeatures'] = ', '.join(reso_fact.get('interiorFeatures', '')) \
                if reso_fact.get('interiorFeatures', '') else ''
            item['parkingFeatures'] = ', '.join(reso_fact.get('parkingFeatures', ''))
            item['sewer'] = ', '.join(reso_fact.get('sewer', '')) if reso_fact.get('sewer', '') else ''
            if reso_fact.get('windowFeatures', ''):
                item['windowFeatures'] = ', '.join(reso_fact.get('windowFeatures', '')) \
                    if reso_fact.get('windowFeatures', '') else ''
            item['constructionMaterials'] = ', '.join(reso_fact.get('constructionMaterials', ''))
            item['exteriorFeatures'] = ', '.join(reso_fact.get('exteriorFeatures', '')) \
                if reso_fact.get('exteriorFeatures', '') else ''
            if reso_fact.get('foundationDetails', ''):
                item['foundationDetails'] = ', '.join(reso_fact.get('foundationDetails', ''))
            item['appliances'] = ', '.join(reso_fact.get('appliances', '')) if reso_fact.get('appliances', '') else ''
            item['propertySubType'] = ', '.join(reso_fact.get('propertySubType', '')) \
                if reso_fact.get('propertySubType', '') else ''
            attributionInfo = details.get('attributionInfo', {})
            item['mlsName'] = attributionInfo.get('mlsName', '')
            item['agentName'] = attributionInfo.get('agentName', '')
            item['agentEmail'] = attributionInfo.get('agentEmail', '')
            item['agentPhoneNumber'] = attributionInfo.get('agentPhoneNumber', '')
            item['listingOffices'] = attributionInfo.get('listingOffices', [{}])[0].get('officeName', '')
            item['listingAgents'] = attributionInfo.get('listingAgents', [{}])[0].get('memberFullName', '')
            item['schools'] = '|'.join([','.join([f'{key}: {value}'
                                                  for key, value in school.items()])
                                        for school in details.get('schools', [{}])])
            item['priceHistory'] = str(details.get('priceHistory', ''))
            item['taxHistory'] = str(details.get('taxHistory', ''))
            item['associations'] = details.get('resoFacts', {}).get('associations', [])
            item['associationFeeIncludes'] = details.get('resoFacts', {}).get('associationFeeIncludes', [])
            yield item
