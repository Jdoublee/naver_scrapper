import scrapy
from naver_scrapper.items import NaverScrapperItem

class NaverSpider(scrapy.Spider):
    name = "naver"
    def start_requests(self):
        urls = [
            "https://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=102&oid=001&aid=0011729190"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_list(self, response):
        url = ""
        yield         
    def parse(self, response):
        item = NaverScrapperItem()
        item['url'] = response.url
        item['content'] = response.xpath("//div[@id='articleBodyContents']//text()").getall()
        item['media'] = response.xpath("//div[@class='press_logo']")
        
        yield item

        # content = response.xpath(
        #     "//div[@id='articleBodyContents']//text()").getall()
        # self.log(content)
