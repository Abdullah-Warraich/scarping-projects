import scrapy
from itertools import product
import string


# crawl sbs_scraper -a state="AL" -O records.csv
class SbsScraperSpider(scrapy.Spider):
    name = "sbs_scraper"
    state = 'DE'
    headers = {
        'authority': 'services.naic.org',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://sbs.naic.org',
        'referer': 'https://sbs.naic.org/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    licenseTypesUrl = "https://services.naic.org/api/licenseeLookup/summary/licenseTypes/{}/{}"
    demographicsUrl = "https://services.naic.org/api/licenseeLookup/summary/demographics/{}?entityType=IND"
    lookupPhoneEmailUrl = "https://services.naic.org/api/licenseeLookup/summary/lookupPhoneEmailWebsite/{}"
    CeInfoUrl = "https://services.naic.org/api/licenseeLookup/summary/ceInfo/{}/{}"
    appointmentsUrl = "https://services.naic.org/api/licenseeLookup/summary/appointments/{}/{}"
    linesOfAuthorityUrl = "https://services.naic.org/api/licenseeLookup/summary/linesOfAuthority/{}"
    details_link = "https://sbs.naic.org/solar-external-lookup/lookup/licensee/" \
                   "summary/{}?jurisdiction={}&entityType=IND&licenseType={}"

    custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        # 'CONCURRENT_REQUESTS_PER_IP': 2,
        'DOWNLOAD_DELAY': 0.2,
        # 'AUTOTHROTTLE_ENABLED': True,
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': ['name', 'residency', 'loas', 'npn', 'businessAddress', 'details_url',
                               'licenseId', 'licenseType', 'licenseTypeCode', 'licenseNumber', 'licenseStatus',
                               'statusDate', 'firstActiveDate', 'effectiveDate', 'expirationDate',
                               'domicileState', 'domicileCountry', 'resident', 'zipcode', 'state', 'phones',
                               "emails", "urls", 'compliant', 'complianceDate', 'CompliantStartDate',
                               'compliantEndDate', 'compliantDesigOver25Years', 'companyName', 'naicno',
                               'appointmentDate', 'lineType', 'examCertDate', 'lineStatus', 'LineStatusDate',
                               'LineEffectiveDate', 'LineExpirationDate'
                               ],
    }

    def __init__(self, state=None, *args, **kwargs):
        super(SbsScraperSpider, self).__init__(*args, **kwargs)
        if state is not None:
            self.state = state
            print(self.state)

    def start_requests(self):
        alphabet = string.ascii_lowercase
        combinations = list(product(alphabet, repeat=1))
        for a in combinations:
            url = f"https://services.naic.org/api/licenseLookup/search?jurisdiction={self.state}&searchType=Licensee" \
                  f"&entityType=IND&lastName={''.join(a)}&residentLicense=Yes"
            yield scrapy.Request(
                url,
                headers=self.headers,
                callback=self.parse,
                meta={'state': self.state}
            )

    def parse(self, response):
        data = response.json()
        for record in data:
            item = dict()
            item['name'] = record.get('name', '')
            item['residency'] = record.get('residency', 'No')
            item['loas'] = record.get('loas', 'NO LINES ASSIGNED')
            item['npn'] = record.get('npn', 0)
            item['businessAddress'] = record.get('businessAddress', '')
            item['details_url'] = self.details_link.format(record.get('licenseNumber', ''), self.state,
                                                           record.get('licenseTypeCode', 'PRO'))

            yield scrapy.Request(
                self.licenseTypesUrl.format(self.state, f"{record.get('licenseNumber', 0)}"),
                method='GET',
                headers=self.headers,
                callback=self.license_types,
                meta={'item': item}
            )

    def license_types(self, response):
        data = response.json()
        item = response.meta.get('item')
        if len(data) > 0:
            item['licenseId'] = data[0].get('licenseId', '')
            item['licenseType'] = data[0].get('licenseType', '')
            item['licenseTypeCode'] = data[0].get('licenseTypeCode', 'PRO')
            item['licenseNumber'] = data[0].get('licenseNumber', '')
            item['licenseStatus'] = data[0].get('licenseStatus', '')
            item['statusDate'] = data[0].get('statusDate', '')
            item['firstActiveDate'] = data[0].get('firstActiveDate', '')
            item['effectiveDate'] = data[0].get('effectiveDate', '')
            item['expirationDate'] = data[0].get('expirationDate', '')

            yield scrapy.Request(
                self.demographicsUrl.format(f"{data[0].get('licenseId', 0)}"),
                method='GET',
                headers=self.headers,
                callback=self.info,
                meta={'licenseId': data[0].get('licenseId', 0), 'item': item}
                )
        else:
            yield item

    def info(self, response):
        data = response.json()
        item = response.meta.get('item')
        item['domicileState'] = data.get('domicileState', '')
        item['domicileCountry'] = data.get('domicileCountry', '')
        item['resident'] = data.get('resident', 'No')
        item['zipcode'] = data.get('businessAddress', '').get('zipcode', '')
        item['state'] = data.get('businessAddress', '').get('state', '')

        yield scrapy.Request(
            self.lookupPhoneEmailUrl.format(f"{response.meta.get('licenseId', 0)}"),
            method='GET',
            headers=self.headers,
            callback=self.contacts,
            meta={'licenseId': response.meta.get('licenseId'),
                  'businessAddress': data.get('businessAddress', self.state).get('state', self.state), 'item': item}
        )

    def contacts(self, response):
        data = response.json()
        item = response.meta.get('item')
        nums = []
        emails = []
        urls = []
        for i in data.get('phones', []):
            nums.append(i['phoneNumber'])
        item['phones'] = '/ '.join(nums)
        for i in data.get('emails', []):
            emails.append(i['emailAddress'])
        item['emails'] = '/ '.join(emails)
        for i in data.get('urls', []):
            urls.append(i['urlAddress'])
        item['urls'] = '/ '.join(urls)

        yield scrapy.Request(
            self.CeInfoUrl.format(response.meta.get('businessAddress'), f"{response.meta.get('licenseId')}"),
            method='GET',
            headers=self.headers,
            callback=self.ceinfo,
            meta={'licenseId': response.meta.get('licenseId'),
                  'businessAddress': response.meta.get('businessAddress'), 'item': item}
        )

    def ceinfo(self, response):
        data = response.json()
        item = response.meta.get('item')
        item['compliant'] = data.get('compliant', '')
        item['complianceDate'] = data.get('complianceDate', '')
        item['CompliantStartDate'] = data.get('startDate', '')
        item['compliantEndDate'] = data.get('endDate', '')
        item['compliantDesigOver25Years'] = data.get('desigOver25Years', '')

        yield scrapy.Request(
            self.appointmentsUrl.format(response.meta.get('businessAddress'), f"{response.meta.get('licenseId')}"),
            method='GET',
            headers=self.headers,
            callback=self.appointments,
            meta={'licenseId': response.meta.get('licenseId'), 'item': item}
        )

    def appointments(self, response):
        data = response.json()
        item = response.meta.get('item')
        company_name = []
        naicno = []
        appointment_date = []
        for i in data['appointments']:
            company_name.append(i.get('companyName', ''))
            naicno.append(i.get('naicno', ''))
            appointment_date.append(i.get('appointmentDate', ''))

        item['companyName'] = '/'.join(company_name)
        item['naicno'] = '/'.join(naicno)
        item['appointmentDate'] = ','.join(appointment_date)

        yield scrapy.Request(
            self.linesOfAuthorityUrl.format(f"{response.meta.get('licenseId')}"),
            method='GET',
            headers=self.headers,
            callback=self.line_of_authority,
            meta={'item': item}
        )

    def line_of_authority(self, response):
        data = response.json()
        item = response.meta.get('item')
        line_type = []
        exam_cert_date = []
        line_status = []
        line_status_date = []
        line_effective_date = []
        line_expiration_date = []
        for i in data:
            line_type.append(i.get('lineType', ''))
            exam_cert_date.append(i.get('examCertDate', ''))
            line_status.append(i.get('lineStatus', ''))
            line_status_date.append(i.get('statusDate', ''))
            line_effective_date.append(i.get('effectiveDate', ''))
            line_expiration_date.append(i.get('expirationDate', ''))

        item['lineType'] = ' / '.join(line_type)
        item['examCertDate'] = ' , '.join(exam_cert_date)
        item['lineStatus'] = ' / '.join(line_status)
        item['LineStatusDate'] = ' , '.join(line_status_date)
        item['LineEffectiveDate'] = ' , '.join(line_effective_date)
        item['LineExpirationDate'] = ' , '.join(line_expiration_date)
        print(item)
        yield item
