# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter

class HeadlessCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):

        # args[0] is (opened) file handler
        # if file is not empty then skip headers
        if os.fstat(args[0].fileno()).st_size > 0:
            kwargs['include_headers_line'] = False

        super(HeadlessCsvItemExporter, self).__init__(*args, **kwargs)

class NaverScrapperPipeline:
    def open_spider(self, spider):
        self.url_to_exporter = {}

    def close_spider(self, spider):
        for exporter in self.url_to_exporter.values():
            exporter.finish_exporting()

    def _exporter_for_item(self, item):
        url = item['url']
        year = item['pub_date'][:4]
        if url not in self.url_to_exporter:
            f = open('newsCrawl-edaily-{year}.csv'.format(year=year), 'ab')
            exporter = HeadlessCsvItemExporter(f)
            exporter.start_exporting()
            self.url_to_exporter[url] = exporter
        return self.url_to_exporter[url]

    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item