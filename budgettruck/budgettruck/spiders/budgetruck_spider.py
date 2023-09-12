import json
import scrapy


class MyntraSpider(scrapy.Spider):
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'FEEDS': {
            'output.csv': {
                'format': 'csv',
                'overwrite': True,  # This will overwrite the file if it already exists
            },
        },
    }
    json_data = {
        'DefaultVehicleClassCode': None,
        'DropOffLocation': 'Washington, DC',
        'FreeMiles': 0,
        'IsAutoPromotion': False,
        'IsFlexible': True,
        'IsLocal': False,
        'IsPartnerURL': False,
        'IsReservationEdit': False,
        'LastChangeDate': None,
        'LastChangeUserId': None,
        'LocationDetails': None,
        'PickUpLocation': 'Las Vegas, NV',
        'RentalLocationDefaultDealer': 0,
        'TruckDetails': None,
        'AccountNumber': None,
        'AccountTypeCode': None,
        'ApplicationType': 'P',
        'AppliedPromotion': None,
        'CUS_GPS_IND': None,
        'CancelFlag': False,
        'CancelReason': None,
        'CancelReasonOther': None,
        'CancelRequested': False,
        'ChargedAmt': 0,
        'CouponID1': '',
        'CouponID2': None,
        'CustomerFollowUpBy': None,
        'CustomerFollowUpDate': '0001-01-01T00:00:00',
        'DestinationDealerNumber': 0,
        'DispatchDealerNumber': 0,
        'DueInDate': '09/11/2023',
        'DueInTime': None,
        'IsNew': False,
        'IsUserPrivacyOptedOut': None,
        'OrigIPAddress': None,
        'PaymentData': None,
        'PickupDate': '09/15/2023',
        'PickupTime': '05:00 PM',
        'PrimaryCustomer': None,
        'ProtectionBundleID': None,
        'ReferenceNumber': None,
        'RentalAmt': 0,
        'RentalDays': 0,
        'RentalMiles': 0,
        'RentalNeed': None,
        'RentalTransactionStageType': None,
        'RentalTransactionType': None,
        'TaxAmt': 0,
        'TaxExemptData': None,
        'TaxSummary': None,
        'TransactionDate': None,
        'TransactionTime': None,
        'VehicleClassCode': None,
        'VehicleMade': None,
        '__ko_mapping__': {
            'ignore': [],
            'include': [
                '_destroy',
            ],
            'copy': [],
            'observe': [],
            'mappedProperties': {
                'DefaultVehicleClassCode': True,
                'DropOffLocation': True,
                'FreeMiles': True,
                'IsAutoPromotion': True,
                'IsFlexible': True,
                'IsLocal': True,
                'IsPartnerURL': True,
                'IsReservationEdit': True,
                'LastChangeDate': True,
                'LastChangeUserId': True,
                'LocationDetails': True,
                'PickUpLocation': True,
                'RentalLocationDefaultDealer': True,
                'TruckDetails': True,
                'AccountNumber': True,
                'AccountTypeCode': True,
                'ApplicationType': True,
                'AppliedPromotion': True,
                'CUS_GPS_IND': True,
                'CancelFlag': True,
                'CancelReason': True,
                'CancelReasonOther': True,
                'CancelRequested': True,
                'ChargedAmt': True,
                'CouponID1': True,
                'CouponID2': True,
                'CustomerFollowUpBy': True,
                'CustomerFollowUpDate': True,
                'DestinationDealerNumber': True,
                'DispatchDealerNumber': True,
                'DueInDate': True,
                'DueInTime': True,
                'IsNew': True,
                'IsUserPrivacyOptedOut': True,
                'OrigIPAddress': True,
                'PaymentData': True,
                'PickupDate': True,
                'PickupTime': True,
                'PrimaryCustomer': True,
                'ProtectionBundleID': True,
                'ReferenceNumber': True,
                'RentalAmt': True,
                'RentalDays': True,
                'RentalMiles': True,
                'RentalNeed': True,
                'RentalTransactionStageType': True,
                'RentalTransactionType': True,
                'TaxAmt': True,
                'TaxExemptData': True,
                'TaxSummary': True,
                'TransactionDate': True,
                'TransactionTime': True,
                'VehicleClassCode': True,
                'VehicleMade': True,
            },
            'copiedProperties': {},
        },
    }

    def __init__(self, city_name=None, pickup_date=None, pickup_time=None, drop_off_location=None, *args, **kwargs):
        super(MyntraSpider, self).__init__(*args, **kwargs)
        self.city_name = city_name
        self.json_data['PickUpLocation'] = city_name
        self.json_data['PickupDate'] = pickup_date
        self.json_data['PickupTime'] = pickup_time
        self.json_data['DropOffLocation'] = drop_off_location
        print(self.json_data)

    name = "truck_spider"
    start_urls = ["https://www.budgettruck.com/"]
    reservation = "https://www.budgettruck.com/API/BudgetTruck.WebAPI/Home/SearchReservation"
    trucks = ("https://www.budgettruck.com/API/BudgetTruck.WebAPI/Truck/GetTrucks?pickupDate"
              "=&dropOffDate=&isEditModel=false")

    def parse(self, response):
        token = response.xpath("//input[@name='__RequestVerificationToken']/@value").get()
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'datacenter=ptc; datacenter=ptc; dnn_IsMobile=False; language=en-US; dtCookie=v_4_srv_1_sn_1D3322DC8A03F748B2BD727294AAD9A4_perc_100000_ol_0_mul_1_app-3Ad92d9779c59e8199_1; .ASPXANONYMOUS=76zb9H_i14PEBVqfzr5gR8PZBqFuXPTore7dB-5XopKtLgUbH-YSTHB0lqrmeDNSGpyNrZjRcKTgQeRn6FmZCOfR6pod6nrbf48-PuI5dlj0X18Qia5a_SPHn5Gp0IGYD1RMyiFZd3LBsDeuggsSSg2; Analytics_VisitorId=1f0e57ec-6470-47e0-8620-e889c899adfb; Analytics=SessionId=f42c823a-96a6-479c-8563-fd95611ecbf0&TabId=56&ContentItemId=-1; __RequestVerificationToken=O-QJtNPaM5eiKJ9pZuHMbL_B32e75qoA6UH26PIQtiewImkZKfJHy5lsR-4CHHvFoiYpKPgQ8ToWGbbgoOKLcQvWVwW0UdgyDkTOILgCVnI1; rxVisitor=1694432009593B6A921IPSPQQQIP6BOUDLE6H65CMC1PJ; dtSa=-; optimizelyEndUserId=oeu1694432020552r0.736091395953504; _gcl_au=1.1.1730360466.1694432022; _ga=GA1.1.67302510.1694432024; _gid=GA1.1.1425768415.1694432024; _dc_gtm_UA-6997633-6=1; _ga=GA1.2.67302510.1694432024; _gid=GA1.2.1425768415.1694432024; _gat_UA-6997633-6=1; _gat_growCR=1; _ga_PRWXCNFHG9=GS1.1.1694432024.1.0.1694432024.60.0.0; bounceClientVisit2357v=N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgO6kB0ARgK4AmA5gKZIBOVAxgNZlsD2AtkRAAaEMxggQAXyA; PickUpLocation=jCRM+4BBPvHfOr39dY9MIA==; PromoCode=; DropOffTime=; _uetsid=16407b80509711ee998d41c83bdd24bd; _uetvid=1640ba40509711ee92cf91bea4fa2e49; QuantumMetricSessionID=76a1365a8c9b3ec3fc1984b228a66ff9; QuantumMetricUserID=5ee47a90c0084df12a8415e3da8e4c74; bounceClientVisit2357=N4IgJglmIFwgrAdgEyoJxoAwBYAcu1dl5tk1sQAaEANylgEYA2c7AZmU2W1LabfjUasUAHsAdgFMA+gHcAhgE9YAFwBOAV0nUAFqIC2kgA7yA5jMgBnAMaiN4ldPlGjAGwiToMAGbzXl7RBreTUVWF9-QLVJS2lJAA8jCGivCIDqZzcPMGlbDSMJcL90kCTrAGt86VdRYJUIQp9iwLLKo2kweRULLslYTmQ2TDQGBmowNVF20W9vDt6iyOpWqusIFWU4ABl5SwACADVJU12qUogKqssVBbgAOQOzianpGbm1jcWS5+nZ6WvbmkWhdytIqvVDLAQJh4DBMJg9gAFACyZ3k4jWrlcIQ8sQCrkk1m6qWaGQxECxOJiHUJ7ikJMiAF9qJZ6HDGUA; PickUpDate=ZbMWgBonZth3LW2jtbo3Kw==; DropOffDate=ZbMWgBonZth3LW2jtbo3Kw==; PickupTime=pcyr9gvESFlloVK1YyIxHg==; IsFlexible=3vEYstofwtzUccPfRLO2nA==; DropOffLocation=sGVPH5n73kgmNeFU3/cGKA==; _ga_PRWXCNFHG9=GS1.2.1694432024.1.1.1694432068.16.0.0; rxvt=1694433868275|1694432009596; dtPC=1$32009588_247h34vKACCQOADCMLCMUMFCMBAQHBUSLJUVUEI-0e0; datacenter=ptc; ASP.NET_SessionId=a2v2y5ni4ag3i4gy1lbnvgjw; DropOffDate=ae+ZrQNihaT0C7KlcRP67Fg5RtcC26AY31E1G81r8s4=; DropOffLocation=sGVPH5n73kgmNeFU3/cGKA==; IsLocal=ckND2uCw7UHDkksEK3cekQ==; PickUpDate=6WoN1wM6+KHRP7/y7ffbKFg5RtcC26AY31E1G81r8s4=; PickUpLocation=jCRM+4BBPvHfOr39dY9MIA==; PickupTime=dR1zGcve6Sa9m8Ll32AP3g==; PromoCode=; QuoteId=VB8wUPZOVXkprLQP6IlDvg==; RentalStage=fci+O7lmXsTDxEdck2RtSA==; dnn_IsMobile=False; language=en-US',
            'ModuleId': '12812',
            'Origin': 'https://www.budgettruck.com',
            'Referer': 'https://www.budgettruck.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TabId': '56',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            '_RequestVerificationToken': token,
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-dtpc': '1$32009588_247h34vKACCQOADCMLCMUMFCMBAQHBUSLJUVUEI-0e0'
        }
        yield scrapy.Request(self.reservation, headers=headers, body=json.dumps(self.json_data),
                             callback=self.start_scraping, method='POST')

    def start_scraping(self, response):
        yield scrapy.Request(self.trucks, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                 'Chrome/116.0.0.0 Safari/537.36'},
                             callback=self.trucks_response, method='GET')

    def trucks_response(self, response):
        trucks = json.loads(response.body.decode('utf-8')).get('trucksSorted', '')
        for truck in trucks:
            item = dict()
            item['NoOfSeats'] = truck.get('NoOfSeats', '')
            item['TruckRate'] = truck.get('TruckRate', '')
            item['TruckClearance'] = truck.get('TruckClearance', '')
            item['TruckInteriorHeight'] = truck.get('TruckInteriorHeight', '')
            item['TruckInteriorLength'] = truck.get('TruckInteriorLength', '')
            item['TruckInteriorWidth'] = truck.get('TruckInteriorWidth', '')
            item['AdditionalFeatures'] = truck.get('AdditionalFeatures', '')
            item['Name'] = truck.get('Name', '')
            item['ImageUrl'] = truck.get('ImageUrl', '')
            item['Description'] = truck.get('Description', '')
            if truck.get('TruckRate', '') is not None and truck.get('TruckRate', '') != 0.0:
                item['TruckRate'] = str(truck.get('TruckRate', '')) + str(truck.get('TruckRateMessage', ''))
            item['TruckUndiscountedRate'] = truck.get('TruckUndiscountedRate', '')
            item['TruckDiscountPercent'] = truck.get('TruckDiscountPercent', '')
            item['SoldOutMessage'] = truck.get('SoldOutMessage', 'Unsoled')
            item['TowingCompatible'] = truck.get('TowingCompatible', False)
            item['AllowsLoadingRamp'] = truck.get('AllowsLoadingRamp', False)
            item['ImageUrl'] = ''.join([self.start_urls[0][0:-2] + truck.get('ImageUrl', '')])

            yield item
