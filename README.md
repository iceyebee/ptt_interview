We will use **scrapy** with a more comprehensive framework for managing web searching. 

# Getting started
`git clone`

`docker`

Dependencies:
* Redis
* MongoDB
    Download older version if your OS is old.
* Python 
* pip
    * pymongo
    * BeautifulSoup4
    * requests
    * scrapy-redis
    * time
    * datetime
    * re
    * logging
    * smtplib
    * ssl

# scrapy framework
What you will see is a scrapy project, as follows:
```
ppt_interview/
    |
    - scrapy.cfg           
    |
    - ptt_interview/ 
       |     
       -  __init__.py
       |
       - items.py
       - middlewares.py
       - pipelines.py 
       - settings.py 
       |
       - spiders/
          |
          -  __init__.py
          |
          -  ptt.py  (the spider)
```
(To create your own project, run this commend:
`$ scrapy startproject ptt_interview`)
# Set up browser settings
IMPORTANT: your spider program will soon face connection problem if you do not set up a proper user-agent setting.

To get your setting as a string: 
1. Go to **View** > **Developer Options** > **Elements**.

2. Once the **Elements** panel is open, 
refresh the webpage, you will see files are generated under **Network**.

3. Go to **Network** > **index.html** > **user-agent** to find your user-agent setting *as a string*.

Here is a good video to copy your user-agent string:
https://www.youtube.com/watch?v=9Z9xKWfNo7k&t=560s

In setting.py:
Search **USER-AGENT** and put in your own setting

In ptt.py:
Search ***your setting*** and replace it with your string.

Now your program will probably work.

# Modify settings.py
Scrapy has a more complete architecture for web crawling, as follows.

BEFORE RUNNING, we need to adjust the settings.py file to connect to DB, extensions, and other custom stuff. 

![](https://i.imgur.com/eBwgZbO.png)

# * To run with MongoDB:
Use: In our project, we use MongoDB to store parsed data by updating (thus, avoiding repetitive inserts)
1. Search **Configure mongodb item pipelines** in settings.py
2. Set `MONGO_URI`, `MONGO_DATABASE`, and the corresponding dictionary of `ITEM_PIPELINES`
(make sure to find the right one!)  
- - - 
If you have not already, install **MongoDB**
Start mongod process and mongo server before running the program.
`$ mongod`
`$ mongo`
Check if mongod process is runing:
`ps -ax | grep mongo`
* For more MongoDB commands and installation instructions, go to https://docs.mongodb.com/manual/administration/install-community (community edition)
- - - 
3. Run scrapy `$scrapy crawl ppt [...]`
4. After running, go to mongo server to see stored data. 
example commands:
`> use ptt_interview`
`> show collections`
`> db.[collection].find().limit(1)`


# * To run with extensions to send notifcation
* First, you need a sender's account info and the receiver email
* Modify the code for extension in middlewares.py, which were made easy by using default signals like *spider_closed* to send a message of run stats when the spider is done as written in the `SendMailWhenDone` class.
* Search **Search Enable or disable your own extensions** in settings.py and uncomment `MYEXT_ENABLED` to run your custom extension. There are also scrapy's default extensions (https://docs.scrapy.org/en/latest/topics/extensions.html#).
* Also, `EXTENSIONS = {'ptt_interview.middlewares.SendMailWhenDone': 80,}` needs to be uncommented.
    
NOTICE: This email notification is not working properly after 2 successful tries. The reason is probably that the gmail mail server allows the connection only for a certain number of times. So, to be improved!

# * To use Redis on master machine:
Use: Good for master-slave mechanism. When running, more data loss are expected with speed improvement using the redis pipeline. [Notes: redis is stored in-memory and can resume last session.]

* The master machine connects to redis (and, maybe, DB) and slave machines can connect to redis and the DB like mongoDB (or other DB) for storing.
* The slave machines help to download requests from and store it back to master’s redis by first getting some urls from master’s redis.

This fundenmentally affects the scrapy framework from requests, scheduler, to item pipelines.

So we need to enable to following lines in the ptt.py spider program, which is also changed to a redis-spider:
* `from scrapy_redis.spiders import RedisSpider`
    * `class PttSpider(RedisSpider):`
        *replacing* `class PttSpider(scrapy.Spider)`
        * `redis_key = "PttInterviewCrawler:some_urls"`

In settings.py:

* Search **Configure redis item pipelines**
* Set `SCHEDULER`, `DUPEFILTER_CLASS` for avoiding receptive data, `SCHEDULER_PERSIST`, `SCHEDULER_QUEUE_CLASS`, `ITEM_PIPELINES`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_ENCODING` for Chinese 
* Remember to set REDIS_HOST with master's IP address:
* Getting IP addresses:
`$ ipconfig getifaddr en1` (Ethernet)
`$ ipconfig getifaddr en0` (Wireless)

See more information here: https://www.jianshu.com/p/93be1d9fc55e

Finally...
1. Install Redis (https://redis.io)
2. Start redis server `$ redis-server --protected-mode no`
3. Run scrapy 
 `$scrapy crawl ppt [...]` (master)
 `$crawl ppt [...]` (slave)
4. Test `$redis-cli -h [master ip addr] `
 example commends: 
 `> KEYS`
 `> LRANGE ptt:items 0 100`
 (*ptt:items* is a set datatype.)
* for more command lines: https://redis.io/commands


# Run ptt.py spider program
The main spider program is ptt.py.

Normally, to run it: `$ scrapy crawl ptt `

However, we added date range arguments.
So please use the following:
`$ scrapy crawl ptt -a start_month=2 -a start_day=24 -a end_month=2 -a end_day=25`
# Input limitations
 The input arguments are currently not error-proof. 
 
 Please enter only values that make sense.
 
 And only works with dates in **Year 2020**...
 
 To be improved...
 
 Also, the ptt.py spider only go through the **101th** and **102th** most popular boards for testing purpose...
 
 To make it go through all popular boards, 
 change this line in ptt.py
 `for b in board_divs[101:102]:`
 to
 `for b in board_divs:`
 to browse through all boards.
 
# More on improvements
Under Development...
* Input error catch
* Enable across-the-years checking
    * Issue: Only month and date at page levels
    * Possible solution: Try going deeper to thread levels to get complete date for `get_top_date()` and `get_update_date()` in ptt.py

* Add more alerts
    * Issue: Continue crawling with no items yield. 
* Understand more about scrapy with Redis
    * Issue: Test master-slave mechanism
        * Comments: The scrapy spider is kinda request-pressured, so spiders can make good use of its request-response mechanism, but not so sure about counting things or public variables in the public area...
    * Issue: It does not work properly if it's restarted too soon.
    * Issue: Display Chinese
* ...and more!