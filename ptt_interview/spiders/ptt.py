# -*- coding: utf-8 -*-
import scrapy
import requests
import re
import time #avoid speed crawling
from datetime import datetime
from bs4 import BeautifulSoup
from ptt_interview.items import PttInterviewItem
#from scrapy_redis.spiders import RedisSpider

class PttSpider(scrapy.Spider):
#class PttSpider(RedisSpider):
    name = 'ptt'
    main_url = "https://www.ptt.cc/bbs/index.html"
    base_url = "https://www.ptt.cc"
    allowed_domains = ['ptt.cc']
    item = PttInterviewItem()
    index_page_number = 0
    # redis_key = "PttInterviewCrawler:some_urls"
    # start_urls = ['url'] is a spider variable that is used as starting url if written

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def start_requests(self):
        time.sleep(2)
        get_main = requests.get(self.main_url, headers \
            = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36"
            })
        main_content = get_main.text
        site_soup = BeautifulSoup(main_content, 'html.parser')
        board_divs = site_soup.find_all('div', class_="board-name")
        for b in board_divs[101:102]:
        #SEARCH ALL BOARDS
        #for b in board_divs:
            self.item['board_name'] = b.text
            #parse each board
            time.sleep(2)
            yield scrapy.Request(self.base_url + "/bbs/" + b.text + "/index.html", \
                callback=self.go_to_board_index, meta={'board_name': b.text})
    def go_to_board_index(self, response):
        #get board index page no
        board_name = response.meta['board_name']
        last_page = response.css('div.btn-group-paging > a::attr(href)')[1].extract()
        page_number = re.findall("index\d+.html", last_page)[0][5:-5]
        #update index pageno and make it current pageno 
        if page_number.isnumeric():
            index_page_number = int(page_number) + 1
            current_page_number = index_page_number
        else:
            current_page_number = 0

        #get variables for page turning loop
            #minimum date entered
        min_date_str = '2020-' + self.start_month + '-' + self.start_day + '--00-00-00'  
        min_date = time.mktime(datetime.strptime(min_date_str, '%Y-%m-%d--%H-%M-%S').timetuple())
            #maximum date entered
        max_date_str = '2020-' + self.end_month + '-' + self.end_day + '--23-59-59'  
        max_date = time.mktime(datetime.strptime(max_date_str, '%Y-%m-%d--%H-%M-%S').timetuple())
            #date of first and last thread on initial page (index page)
        date_dict = self.get_dates(response.url)
        update_date = self.get_update_date(date_dict, len(date_dict.keys())-4)
        top_date = self.get_top_date(date_dict)
        
        #write turning-page logic and how it goes to page_parse function
        while(update_date >= min_date):
            time.sleep(2)
            print("Starting a page...")

            if min_date > top_date: #just some data on this page
                #search this page
                yield scrapy.Request(self.base_url + "/bbs/" + board_name + "/index" + str(current_page_number) + ".html", \
                     callback=self.parse_page, meta={'min_date':min_date, 'max_date':max_date})
                #then done
                break
            else: #min_date < top_date
                if max_date > top_date: #some data on this page and maybe more next page
                    #search this page
                    yield scrapy.Request(self.base_url + "/bbs/" + board_name + "/index" + str(current_page_number) + ".html", \
                        callback=self.parse_page, meta={'min_date':min_date, 'max_date':max_date})
                    #go to next page
                    current_page_number = current_page_number - 1
                    #update dates of first and last threads on this page
                    date_dict = self.get_dates("{base_url}/bbs/{board_name}/index{current_page_number}.html"\
                     .format(base_url=self.base_url, board_name=board_name, current_page_number=current_page_number))
                    update_date = self.get_update_date(date_dict, len(date_dict.keys()))
                    top_date = self.get_top_date(date_dict)
                else: #out of range for this page but maybe next page
                    #directly go to next page
                    current_page_number = current_page_number - 1
                    #update dates of first and last threads on this page
                    date_dict = self.get_dates("{base_url}/bbs/{board_name}/index{current_page_number}.html"\
                     .format(base_url=self.base_url, board_name=board_name, current_page_number=current_page_number))
                    update_date = self.get_update_date(date_dict, len(date_dict.keys()))
                    top_date = self.get_top_date(date_dict)
    def parse_page(self, response):
        #get threads in first page
        min_date = response.meta['min_date']
        max_date = response.meta['max_date']
        #for every thread, if the date is right and title is not empty, go on to parse_thraed()
        for t in response.css('div.r-ent'):
            time.sleep(2)
            publishTime_str = '2020/' + t.css('div.meta > div.date ::text')[0].extract().replace(' ', '0') + '--00-00-00'  
            publishTime = time.mktime(datetime.strptime(publishTime_str, '%Y/%m/%d--%H-%M-%S').timetuple())
            if publishTime >= min_date and publishTime < max_date and len(t.css('div.title > a::attr(href)')) > 0:
                self.item['canonicalUrl'] = self.base_url + t.css('div.title > a::attr(href)')[0].extract()
                yield scrapy.Request(self.item['canonicalUrl'], callback=self.parse_thread)
    #continue to parse thread and get our variables
    def parse_thread(self, response):
        time.sleep(1)
        #getting some variables
            # This is designed for the current ptt website
            # CHANGE IF APPLICABLE for variables grabbed in this array
        thread_info = []
        comments_dict = {}
        for i in response.css('div.article-metaline > span.article-meta-value ::text'):
            thread_info.append(i.extract())
        self.item['authorId'] = re.sub(r'\(.*\)', '', thread_info[0])[:-1]
        self.item['authorName'] = re.search( "\((.*)\)" , thread_info[0]).group(1)
        self.item['title'] = thread_info[1]
        self.item['publishedTime'] = int(round(time.mktime(datetime.strptime(thread_info[2], '%c').timetuple())*1000,0))
        xpath1 = '//div[@id="main-content"]/text() | //div[@id="main-content"]/span[@class != "f2"]/text()'
        self.item['content'] = response.xpath(xpath1).extract()
        self.item['canonicalUrl'] = response.url
        createdTime_dateTime = datetime.fromtimestamp(int(round(self.item['publishedTime']/1000,0)))
        self.item['createdTime'] = createdTime_dateTime.strftime("%Y-%m-%dT%H:%M:%S") + '.220+08:00' 
        
        #start processing comments
            #format: comments_dict = {"commentId": 
                #{"commentContent":"commentContent",
                #"commentTime":"commentTime"}
                # }   
        commentTime_list = []
        for c in response.css('div.push'):
            commentTime_str = '2020/' + c.css("span.push-ipdatetime ::text")[0].extract()[1:-1] + ':00'
            commentTime = time.mktime(datetime.strptime(commentTime_str, '%Y/%m/%d %H:%M:%S').timetuple())
            commentTime = int(round(commentTime*1000,0))
            commentTime_list.append(commentTime)
            comments_dict[c.css("span.push-userid ::text")[0].extract()] = \
                {'commentContent': c.css("span.push-tag ::text")[0].extract() + c.css("span.push-content ::text")[0].extract(), \
                'commentTime': commentTime}
        self.item['comments'] = comments_dict      

        #use max commentTime for publishTime
        if len(commentTime_list) > 0:
            updateTime_dateTime = datetime.fromtimestamp(int(round(max(commentTime_list)/1000,0)))
            self.item['updateTime'] = updateTime_dateTime.strftime("%Y-%m-%dT%H:%M:%S") + '.220+08:00'
        else:
            self.item['updateTime'] = ''

        #display the variables in terminal    
        yield self.item
    
    #get_dates, get_top_dates, get_update_dates are
    #used for page searching logic by go_to_board_index;
    
    #CURRENTLY UNDER DEVELOPMENT TO WORK FOR SEARCHING DATA 
    #OVER THE YEARS. NOW ONLY AVAILABLE FOR SEARCHING DATES 
    #IN 2020. HOWEVER, YOU CAN MANUALLY EDIT THE VARIABLE year 
    #IN get_top_dates & get_update_dates AND RUN AGAIN TO 
    #SEARCH FOR A DIFFERENT YEAR

    #First, crawl all dates on the given page by BeautifulSoup
    def get_dates(self, url):
        time.sleep(2)
        get_next_pg_txt = requests.get(url, headers \
                            = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel \
                            Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/72.0.3626.96 Safari/537.36" }).text
        dates = BeautifulSoup(get_next_pg_txt, 'html.parser').select("div.date")
        #dates = BeautifulSoup(get_next_pg_txt, 'html.parser').select("div.title")
        date_dict = {}
        for i in range(0, len(dates)):
            date_dict[i+1]=dates[i].text
            #date_dict[i]=dates[i].select_one("a").get('href')
        return date_dict
    def get_top_date(self, date_dict):
        #time.sleep(2)
        top_date = date_dict[1].replace(' ', '0')
        #get_thread_txt = requests.get(self.base_url+top_date, headers \
                        #= {"User-Agent": "Mozilla/5.0 (Macintosh; Intel \
                        #Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) \
                        #Chrome/72.0.3626.96 Safari/537.36" }).text
        #top_date_str = BeautifulSoup(get_thread_txt, 'html.parser').select("span.article-meta-value")[3].text
        year = 2020
        top_date_str = "{year}/{date}".format(year=year, date=top_date)
        #top_date_timestamp = time.mktime(datetime.strptime(top_date_str, '%c').timetuple())
        top_date_timestamp = time.mktime(datetime.strptime(top_date_str, '%Y/%m/%d').timetuple())
        return top_date_timestamp
    def get_update_date(self, date_dict, index):
        #time.sleep(2)
        update_date = date_dict.get(index).replace(' ', '0')
        #get_thread_txt = requests.get(self.base_url+update_date, headers \
                #= {"User-Agent": "Mozilla/5.0 (Macintosh; Intel \
                #Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) \
                #Chrome/72.0.3626.96 Safari/537.36" }).text
        #update_date_str = BeautifulSoup(get_thread_txt, 'html.parser').select("span.article-meta-value")[3].text
        year = 2020
        update_date_str = "{year}/{date}".format(year=year, date=update_date)
        #update_date_timestamp = time.mktime(datetime.strptime(update_date_str, '%c').timetuple())
        update_date_timestamp = time.mktime(datetime.strptime(update_date_str, '%Y/%m/%d').timetuple())
        return update_date_timestamp

    """
    if self.clear_all:
        self.crawler.engine.slot.scheduler.df.clear()
        self.crawler.engine.slot.scheduler.queue.clear()
        if 'Bandwidth exceeded' in response.body:
            raise CloseSpider('bandwidth_exceeded')
    """
