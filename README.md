We will use **scrapy** with a more comprehensive framework for managing web searching. 

# Getting started
`$ git clone https://github.com/iceyebee/ptt_interview.git`

You can set up the work environment using docker. 
`$ docker-compose up`

or, manually install:

`$ cd ptt_interview/ptt_interview/`

`$ pip3 install -r requirement.txt`

Dependencies:
* Redis
* MongoDB
 Download older version if your OS is old.
* Python 
* pip3
    * scrapy
    * pymongo
    * BeautifulSoup4
    * requests
    * scrapy-redis
    * datetime

---

example docker-compose.yml file:
```
version 3
services:
    scrapy-app:
        build:
            - context: .
            - dockerfile: /Dockerfile 
        image: python:latest
        volume:
           - .:/code
        depends_on:
           - redis
           - mongo
    redis:
        container-name: myapp-redis
        image: redis
        ports:
          - 6379:6379
        volume: 
          - redis_data:/data
        command: redis-server /usr/local/etc/redis/redis.conf
    mongo:
        container-name: myapp-mongo
        image: mongo
        ports:
         - 27017:27017
        volume:
         - ./mongo/db:/data/db
volume:
    redis_data:

```
Dockerfile
```
From python:latest
COPY . /code
WORKDIR /code
RUN pip3 install -r requirement.txt
```
---
# scrapy framework
What you will see is a scrapy project, as follows:
```
ppt_interview/
    |
    - scrapy.cfg
    |
    - docker-compose.yml         
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
       - (requirement.txt)
       - (Dockerfile)
       |
       - spiders/
          |
          -  __init__.py
          |
          -  ptt.py  (the spider)
```
(To create your own project, run this commend:
`$ scrapy startproject [new project name]`)
# Set up browser settings
IMPORTANT: your spider program will soon face some connection problems if you do not set up a proper **user-agent** setting.

To get your setting as a string: 
1. Go to **View** > **Developer Options** > **Elements**.

2. Once the **Elements** panel is open, 
refresh the webpage, you will see files being generated under **Network**.

3. Go to **Network** > **index.html** > **user-agent** to find your user-agent setting *as a string*.

Here is a good video to learn how to copy your user-agent string:
https://www.youtube.com/watch?v=9Z9xKWfNo7k&t=560s

In ***setting.py***:
Search **USER-AGENT** and put in your own setting

In ***ptt.py***:
Search ***your setting*** and replace it with your string.

Now your program will probably work. You may go to the **Run** section of this page to start testing and come back later to modify ***settings.py***. 

# Modify settings.py
Scrapy has a more complete architecture for web crawling, as follows. 

![](https://i.imgur.com/eBwgZbO.png)

BEFORE RUNNING, we need to decide how to adjust the ***settings.py*** in order to connect to DB, extensions, and other custom stuff.

Here is an example from this project:

# * To run with MongoDB:
In our project, we use MongoDB to store parsed data by updating (thus, avoiding repetitive inserts).
1. Search **Configure mongodb item pipelines** in ***settings.py***
2. Set `MONGO_URI`, `MONGO_DATABASE`, and the corresponding dictionary of `ITEM_PIPELINES` by uncommenting them (make sure to find the right ITEM_PIPELINES!).

- - - 
If you have not already, install **MongoDB**.

Start mongod process and mongo server before running the program.

`$ mongod`

`$ mongo`

Check if mongod process is runing:

`ps aux | grep -v grep | grep mongod`
* For more MongoDB commands and installation instructions, go to https://docs.mongodb.com/manual/administration/install-community (community edition)
- - - 
3. Go to scrapy folder. Run scrapy `$scrapy crawl ppt [...]`
4. After running, go to mongo server to see stored data. 

Example commands:

`> use ptt_interview`

`> show collections`

`> db.[collection].find().limit(1)`

***Alternatively***, if your docker is working well  (`$docker run hello-world`), the redis-cli can also be started by the ***docker-compose.yml*** file for this project or started alone by the following docker commands:

`$ docker pull mongo`

`$ docker run -d --name mymongo -p 27017-27019:27017-27019 mongo`

`$ docker exec -it mymongo bash`

# * To run with extensions to send notifcations
* First, you need sender's account info and the receiver's email
* See the modified code for custom extension in ***middlewares.py***, which are made easy by using default signals like *spider_closed* to perform actions in the `SendMailWhenDone` class.
* Search **Enable or disable your own extensions** in ***settings.py*** and uncomment `MYEXT_ENABLED` to run with custom extension. There are also scrapy's default extensions (https://docs.scrapy.org/en/latest/topics/extensions.html#).
* Also, `EXTENSIONS = {'ptt_interview.middlewares.SendMailWhenDone': 80,}` needs to be uncommented.
    
NOTICE: This email notification is not working properly after 2 successful tries. The reason is probably that the gmail mail server allows the connection only for a certain number of times. So, to be improved!

# * To use Redis on master machine:
Redis is good for the master-slave mechanism. When running, more data loss are expected with speed improvement using the Redis pipeline. 

* The master machine connects to Redis (and, maybe, a database); slave machines can connect to Redis and database like mongoDB for storing.
* The slave machines help to download requests from and store it back to master’s Redis by first getting some urls from master’s Redis.

This fundenmentally affects the scrapy framework from requests, scheduler, to item pipelines.

So we need to add the following lines in the ***ptt.py*** spider program, which is also changed to a redis-spider:
* `from scrapy_redis.spiders import RedisSpider`
    * `class PttSpider(RedisSpider):`
        *replacing* `class PttSpider(scrapy.Spider)`
        * `redis_key = "PttInterviewCrawler:some_urls"`

In ***settings.py***:

* Search **Configure redis item pipelines**
* Set `SCHEDULER`, `DUPEFILTER_CLASS` for avoiding receptive data, `SCHEDULER_PERSIST`, `SCHEDULER_QUEUE_CLASS`, `ITEM_PIPELINES`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_ENCODING` for Chinese (uncomment them)
* Remember to set REDIS_HOST with master's IP address:
    * Getting IP addresses:
    
    `$ ipconfig getifaddr en1` (Ethernet)
    
    `$ ipconfig getifaddr en0` (Wireless)

Finally...
1. Install Redis (https://redis.io/topics/quickstart)
2. Put your IP address in the conf file as `bind [IP address]` and comment out the original bind setting. 
4. Start redis server 
`$ redis-server --protected-mode no`
5. Go to scrapy folder. Run scrapy 
 `$scrapy crawl ppt [...]` (master)
 `$crawl ppt [...]` (slave)
4. Test `$redis-cli -h [master ip addr] `.

 example commends: 
 
 `> KEYS`

 `> LRANGE ptt:items 0 100`
 
 (*ptt:items* is a set datatype.)
* for more command lines: https://redis.io/commands


# Run ptt.py spider program
The main spider program is ***ptt.py***.

Normally, to run it: `$ scrapy crawl ptt `

However, we added date range arguments.
So please use the following: (i.e. for 2/24-2/25)

`$ scrapy crawl ptt -a start_month=2 -a start_day=24 -a end_month=2 -a end_day=25`

...where *start_month* + *start_day* &  *end_month* + *end_day* are of your own choice.
# Input limitations
 The arguments (*start_month*, *start_day*, *end_month*, *end_day*) are currently not error-catched. 
 
 Please enter only values that make sense.
 
 And only works with dates in **Year 2020**...
 
 To be improved...
 
 Also, the ***ptt.py*** spider only go through the **101th** and **102th** most popular boards for testing purpose...
 
 To make it go through all popular boards, 
 change this line in ***ptt.py***

 `for b in board_divs[101:102]:`

 to

 `for b in board_divs:`
 
 to browse through all boards.
 
# More on improvements
More could be under development...
* Input error catches
* Enable across-the-years searching
    * Issue: Only getting month and date at the page level
    * Possible solution: Try going deeper to thread levels to get complete date format for `get_top_date()` and `get_update_date()` in ***ptt.py***

* Add more alerts
    * Issue: Alerts are needed for nonstop crawling attempts with no items yield
* Understand more about scrapy with Redis
    * Issue: Test master-slave mechanism
        * Comments: The scrapy spider is kinda request-pressured, so spiders can make good use of the **request-response** mechanism, but not so sure about counting things or public variables in the public area...
    * Issue: It does not work properly if it's restarted too soon.
    * Issue: Problem with displaying Chinese in the Redis server terminal
* Complete docker development
    * Issue: Docker system requirements cannot be met with current Home PC.
* ...and more!