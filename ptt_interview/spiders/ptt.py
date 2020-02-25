# -*- coding: utf-8 -*-
import scrapy
import requests
import time #avoid speed crawling
from bs4 import BeautifulSoup
from ptt_interview.items import PttInterviewItem

#from scrapy_redis.spiders import RedisSpider

class PttSpider(scrapy.Spider):
#class PttSpider(RedisSpider):
    name = 'ptt'
    main_url = "https://www.ptt.cc/bbs/index.html"
    base_url = "https://www.ptt.cc"
    allowed_domains = ['ptt.cc']
    # redis_key = "PttInterviewCrawler:some_urls"
    #start_urls = ['https://www.ptt.cc/bbs/index.html']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def start_requests(self):
        """
        time.sleep(2)
        get_main = requests.get(self.main_url, headers \
            = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36"
            })
        main_content = get_main.text
        site_soup = BeautifulSoup(main_content, 'html.parser')
        board_divs = site_soup.find_all('div', class_="board-name")
        for b in board_divs[101:102]:
        """
        time.sleep(2)
        yield scrapy.Request(self.base_url + "/bbs/" + "Key_Mou_Pad" + "/index.html", headers \
            = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36" \
            }, callback=self.parse_board)
    def current_page(self, response):
    def parse_board(self, response):
        time.sleep(2)
        item = PttInterviewItem()
        #get threads in first page
        for t in response.css('div.r-ent'): 
            if t.css('div.meta > div.date ::text')[0].extract() == ' %s/%s'%(self.month, self.day) and len(t.css('div.title > a::attr(href)')) > 0:
                item['thread_url'] = self.base_url + t.css('div.title > a::attr(href)')[0].extract()
                item['board_name'] = response.url
                #item['title'] = t.css('div.title a::text')[0].extract()
                yield scrapy.Request(item['thread_url'], headers \
                    = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36" \
                    }, callback=self.parse_thread)
        # (1) turn pages
        # (2) search 10 pages, if no result, stop search
        # (3) data quality
        # (4) dockerize
        # (5) start writing
    #continue to parse thread
    def parse_thread(self, response):
        item = PttInterviewItem()
        thread_info = []
        comments_dict = {"commentId": {"commentContent":"commentContent", \
            "commentTime":"commentTime"}}            
        #put thread info
        for i in response.css('div.article-metaline > span.article-meta-value ::text'):
            thread_info.append(i.extract())
        item['authorId'] = thread_info[0]
        #authorName
        item['title'] = thread_info[1]
        #publishedTime
        #content
        item['canonicalUrl'] = response.url
        item['createdTime'] = thread_info[2] 
        for c in response.css('div.push'):
            comments_dict[c.css("span.push-userid ::text")[0].extract()] = \
                {'commentContent': c.css("span.push-content ::text")[0].extract(), \
                'commentTime': c.css("span.push-ipdatetime ::text")[0].extract()}
        #item['updateTime']
        item['comments'] = comments_dict      
        yield item

        
    """
    if self.clear_all:
        self.crawler.engine.slot.scheduler.df.clear()
        self.crawler.engine.slot.scheduler.queue.clear()
        if 'Bandwidth exceeded' in response.body:
            raise CloseSpider('bandwidth_exceeded')
    """
