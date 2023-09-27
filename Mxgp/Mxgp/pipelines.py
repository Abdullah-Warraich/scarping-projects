from scrapy.exporters import CsvItemExporter


class MyCsvExportPipeline(object):
    def __init__(self):
        self.select_option = None

    def open_spider(self, spider):
        self.select_option = {}

    def close_spider(self, spider):
        for exporter in self.select_option.values():
            exporter.finish_exporting()

    def _exporter_for_item(self, item):
        select = item['select_result']
        item.pop('select_result')
        if select not in self.select_option:
            f = open('{}.csv'.format(select), 'wb')
            exporter = CsvItemExporter(f)
            exporter.start_exporting()
            self.select_option[select] = exporter
        return self.select_option[select]

    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item
