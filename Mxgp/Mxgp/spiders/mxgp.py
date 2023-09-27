import csv
from email import encoders
from email.mime.base import MIMEBase
import scrapy
from ..pipelines import MyCsvExportPipeline
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scrapy import signals


class MxgpSpider(scrapy.Spider):
    final_items_list = []
    name = "mxgp_spider"
    name1 = ''
    brand = ''
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'CUNCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
        # 'FEEDS': {
        #     'output.csv': {
        #         'format': 'csv',
        #         'overwrite': True,  # This will overwrite the file if it already exists
        #     },
        # },
        'ITEM_PIPELINES': {
            MyCsvExportPipeline: 1,
        },
    }

    def __init__(self, *args, **kwargs):
        super(MxgpSpider, self).__init__(*args, **kwargs)

    def spider_idle(self, spider):
        sender_email = "19011519-085@uog.edu.pk"
        receiver_email = "19011519-085@uog.edu.pk"
        password = "devcbkzydzjlodfi"
        subject = "Subject of the Email"
        message = "This is the email message."

        # Create a MIME message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        attachment = open('Analysis.csv', "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % 'Analysis.csv')
        msg.attach(part)

        msg.attach(MIMEText(message, "plain"))

        # Establish a secure SMTP connection to Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print("Email sent successfully.")

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "windy-pier-399908-12ed6e422838.json", scope  # Replace with your credentials file
        )
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open('mysheet')  # Replace with your sheet name
        worksheet = spreadsheet.get_worksheet(0)  # Use the first worksheet or specify the index
        # Read the CSV file from local storage
        csv_data = []
        with open('Analysis.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                csv_data.append(row)
        # Update the entire worksheet with the CSV data
        worksheet.update('A1', csv_data)
        print("Data added to Google Sheet.")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MxgpSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        return spider

    def start_requests(self):
        url = "https://results.mxgp.com/reslists.aspx"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                      'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        yield scrapy.Request(url=url, headers=headers, method='GET', callback=self.parse)

    def parse(self, response, **kwargs):
        # All code for scraping
        select_result = response.xpath('//select[@id="SelectResult"]/option[@selected= "selected"]/text()').get()
        if select_result == "Classification":
            print(select_result)
            records = response.xpath('//tr[3]/td[@class = "mxmiddle"]/table/tr')
            if records:
                records.pop()
                columns = records[0].xpath('./td/text()').getall()
                records.pop(0)
                for record in records:
                    item = dict()
                    row = record.xpath('./td//text()').getall()
                    for i in range(0, len(row)):
                        item[columns[i]] = row[i]
                    item['select_result'] = select_result
                    yield item
        elif select_result == "Lap Chart":
            print(select_result)
            records = response.xpath('//tr[3]/td[@class = "mxmiddle"]/table/tr')
            if records:
                columns = records[0].xpath('./td/text()').getall()
                records.pop(0)
                for record in records:
                    item = dict()
                    row = record.xpath('./td/text()').getall()
                    for i in range(0, len(columns)):
                        item[columns[i]] = row[i]
                    item[' '] = row[-2]
                    item['  '] = row[-1]
                    item['select_result'] = select_result
                    yield item
        elif select_result == "Analysis":
            print(select_result)
            tables = response.xpath('//tr[3]/td/table/tr/td/table')
            columns = []
            for table in tables:
                selector_rows = table.xpath('./tr')
                for selector_row in range(0, len(selector_rows)):
                    row = selector_rows[selector_row].xpath('.//text()').getall()
                    if (selector_row in [0, 1, 2] and table.xpath('./tr//text()').get() ==
                            tables[0].xpath('./tr//text()').get()):
                        if self.name1 == '' or self.brand == '':
                            if selector_row == 0:
                                self.name1 = row[0]
                            elif selector_row == 1:
                                self.brand = row[0]
                        columns.extend(row)
                    else:
                        item = dict()
                        if len(row) > 1:
                            item[self.name1] = columns[0]
                            item[self.brand] = columns[1]
                            if(len(columns)-len(row)) > 2:
                                row.insert(1, '')
                            for i in range(0, len(row)):
                                item[columns[i+2]] = row[i]
                            item['select_result'] = select_result
                            yield item
                        else:
                            if selector_row == 0:
                                columns[0] = row[0]
                            elif selector_row == 1:
                                columns[1] = row[0]
        elif select_result == "GP Classification":
            print(select_result)
            records = response.xpath('//tr[3]/td[@class = "mxmiddle"]/table/tr')
            if records:
                columns = records[0].xpath('./td/text()').getall()
                records.pop(0)
                for record in records:
                    item = dict()
                    row = record.xpath('./td/text()').getall()
                    for i in range(0, len(row)):
                        item[columns[i]] = row[i]
                    item['select_result'] = select_result

                    yield item
        elif select_result == "World Championship Classification":
            print(select_result)
            records = response.xpath('//tr[3]/td[@class = "mxmiddle"]/table/tr')
            if records:
                columns = records[0].xpath('./td//text()').getall()
                for i in range(0, len(columns)-1):
                    for j in range(i+1, len(columns)):
                        if columns[i] == columns[j]:
                            columns[j] = columns[i]+' '

                records.pop(0)
                for record in records:
                    item = dict()
                    row = record.xpath('./td')
                    n_row = []
                    for r in row:
                        n_row.append(','.join(r.xpath('.//text()').getall()))
                    row = n_row
                    for i in range(0, len(columns)):
                        item[columns[i]] = row[i]
                    item['select_result'] = select_result
                    yield item
        elif select_result == "Manufacturers Classification":
            print(select_result)
            records = response.xpath('//tr[3]/td[@class = "mxmiddle"]/table/tr')
            if records:
                columns = records[0].xpath('./td//text()').getall()
                for i in range(0, len(columns)-1):
                    for j in range(i+1, len(columns)):
                        if columns[i] == columns[j]:
                            columns[j] = columns[i]+' '

                records.pop(0)
                for record in records:
                    item = dict()
                    row = record.xpath('./td')
                    n_row = []
                    for r in row:
                        n_row.append(','.join(r.xpath('.//text()').getall()))
                    row = n_row
                    columns = columns[:len(row)]
                    for i in range(0, len(columns)):
                        item[columns[i]] = row[i]
                    item['select_result'] = select_result
                    yield item

        # All code about pagination
        data = dict()
        data['__EVENTTARGET'] = response.xpath('//input[@id= "__EVENTTARGET"]/@value').get()
        data["__EVENTARGUMENT"] = response.xpath('//input[@id= "__EVENTARGUMENT"]/@value').get()
        data["__LASTFOCUS"] = response.xpath('//input[@id= "__LASTFOCUS"]/@value').get()
        if data["__LASTFOCUS"] is None:
            data["__LASTFOCUS"] = ''
        if data["__EVENTARGUMENT"] is None:
            data["__EVENTARGUMENT"] = ''
        if data["__EVENTTARGET"] is None:
            data["__EVENTTARGET"] = ''
        data["__VIEWSTATE"] = response.xpath('//input[@id= "__VIEWSTATE"]/@value').get()
        data['__VIEWSTATEGENERATOR'] = response.xpath('//input[@id= "__VIEWSTATEGENERATOR"]/@value').get()
        data['__EVENTVALIDATION'] = response.xpath('//input[@id= "__EVENTVALIDATION"]/@value').get()
        inputs = response.xpath('//form[@id="Form1"]/table/tbody/tr[2]/td/select')
        all_data = dict()
        for inpt in inputs:
            all_data[inpt.xpath('./@id').get()] = inpt.xpath('./option/@value').getall()
            data[inpt.xpath('./@id').get()] = inpt.xpath('./option[@selected= "selected"]/@value').get()
        keys = list(all_data.keys())
        key = keys.pop()
        if data[key] != all_data[key][-1]:
            index = all_data[key].index(data[key])
            data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index+2)}]/@value').get()
        else:
            # return
            key = keys.pop()
            if data[key] != all_data[key][-1]:
                index = all_data[key].index(data[key])
                data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index + 2)}]/@value').get()
            else:
                key = keys.pop()
                if data[key] != all_data[key][-1]:
                    index = all_data[key].index(data[key])
                    data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index + 2)}]/@value').get()
                else:
                    key = keys.pop()
                    if data[key] != all_data[key][-1]:
                        index = all_data[key].index(data[key])
                        data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index + 2)}]/@value').get()
                    else:
                        if keys:
                            key = keys.pop()
                            if data[key] != all_data[key][-1]:
                                index = all_data[key].index(data[key])
                                data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index + 2)}]/@value').get()
                            else:
                                if keys:
                                    key = keys.pop()
                                    if data[key] != all_data[key][-1]:
                                        index = all_data[key].index(data[key])
                                        data[key] = inputs.xpath(f'//*[@id="{key}"]/option[{(index + 2)}]/@value').get()
                                    else:
                                        return

        print(data)
        yield scrapy.FormRequest(
            url="https://results.mxgp.com/reslists.aspx", formdata=data, callback=self.parse)
