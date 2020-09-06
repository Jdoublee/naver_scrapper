import datetime
from datetime import date, timedelta
import pandas as pd
import re

import scrapy
from naver_scrapper.items import NaverScrapperItem
from naver_scrapper.utils import get_content


class NaverSpider(scrapy.Spider):
    name = "naver"
    def start_requests(self):
        base_url = "https://search.naver.com/search.naver?&where=news&query="

        yield scrapy.Request(url=base_url, callback=self.parse_date)

    def parse_date(self, response):
        base_url = "https://search.naver.com/search.naver?&where=news&query="
        url_press_search='&mynews=1' #언론사별 검색 활성화

        url_1="&sort="
        url_2="&photo="
        url_3="&nso=p:from"
        url_4="to"
        url_5="&refresh_start=1"

        url_press="&news_office_checked="

        query="금리"
        start_date = pd.to_datetime('20050101', format='%Y%m%d') # 검색을 시작할 날짜
        end_date = pd.to_datetime('20051231', format='%Y%m%d') # 검색을 종료할 날짜
        day_count = (end_date - start_date).days + 1

        sort="2" # 0: 관련도순 , 1: 최신순 , 2:오래된 순
        photo="0" # 0: 전체, 1: 포토기사 , 2: 동영상기사, 3: 지면기사, 4: 보도자료
        press_num="1001"
        # 연합뉴스 : 1001, 이데일리 : 1018, 연합인포맥스 : 2227

        for start_date_tmp in [start_date + timedelta(n) for n in range(0, day_count+1, 30)]:
            end_date_tmp = min(start_date_tmp + timedelta(29), end_date)

            sd = start_date_tmp.strftime('%Y%m%d') # 검색을 시작할 날짜
            ed = end_date_tmp.strftime('%Y%m%d') # 검색을 종료할 날짜

            url = base_url+query+url_1+sort+url_2+photo+url_3+sd+url_4+ed+url_press_search

            yield scrapy.Request(url=url, callback=self.parse, cookies={'news_office_checked':press_num}, meta={'dont_merge_cookies': False})
    
    def parse(self, response):
        for url,pub,dates,title in zip(response.css('a._sp_each_title::attr(href)').extract(),response.css('._sp_each_source::text').extract(),response.css('dd.txt_inline::text').re(r'\d{4}.\d{2}.\d{2}'),response.css('a._sp_each_title::attr(title)').extract()):
            if 'zdnet' not in url:
                # TCP timeout error 로 인하여 걸러냄
                yield scrapy.Request(url, callback=self.parse_page, meta={'pub_date':dates,'publisher':pub})
            
            next_page = response.css('div.paging a.next::attr(href)').get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_page(self,response):
        item = NaverScrapperItem()        
        item['title']=response.css('head title::text').extract_first()
        item['content']=get_content(response.text)
        dates=response.meta['pub_date'].replace('.','-')
        item['pub_date']=dates
        item['url']=response.url

        yield item