# scrapy_rabbitmq
scrapy框架的RabbitMQ调度器
rabbitmq的scrapy分布式爬虫

修改自 [scrapy-rabbitmq-link](https://raw.githubusercontent.com/mbriliauskas/scrapy-rabbitmq-link)

修改支持pika1.0.0版本
去除延迟10s执行限制
## Installation

Using pip, type in your command-line prompt

```
pip install scrapy-rabbitmq-link
```
 
Or clone the repo and inside the scrapy-rabbitmq-link directory, type

```
python setup.py install
```

## Usage

### Step 1: In your scrapy settings, add the following config values:

```
# Enable RabbitMQ scheduler
SCHEDULER = "scrapy_rabbitmq.scheduler.SaaS"

# Provide AMQP connection string
RABBITMQ_CONNECTION_PARAMETERS = 'amqp://guest:guest@localhost:5672/'

# Set response status codes to requeue messages on
SCHEDULER_REQUEUE_ON_STATUS = [500]

# Middleware acks RabbitMQ message on success
DOWNLOADER_MIDDLEWARES = {
    'scrapy_rabbitmq.middleware.RabbitMQMiddleware': 999
}

```

### Step 2: Add request building method to Spider : _make_request

#### Example: custom_spider.py



```
import scrapy


class CustomSpider(scrapy.Spider):
    name = 'custom_spider'    
    amqp_key = 'test_urls'

    def _make_request(self, mframe, hframe, body):
        url = body.decode()
        return scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        item = ... # parse item
        yield item

``` 

`amqp_key` serves as queue name in spider.


### Step 3: Push URLs to RabbitMQ

Push url list to scrape from.

#### Example: push_urls_to_queue.py

```
#!/usr/bin/env python
import pika
import settings

connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_CONNECTION_PARAMETERS))
channel = connection.channel()

# set queue name
queue_key = 'target_urls'

# publish links to queue
with open('urls.txt') as f:
    for url in f:
        url = url.strip(' \n\r')
        channel.basic_publish(exchange='',
                        routing_key=queue_key,
                        body=url,
                        pika.BasicProperties(
                            content_type='text/plain',
                            delivery_mode=2
                        ))

connection.close()

```


### Step 4: Run spider using [scrapy client](http://doc.scrapy.org/en/1.0/topics/shell.html)

```
scrapy crawl custom_spider
```

HAPPY SCRAPING !!!


## Contributing and Forking

See [Contributing Guidlines](CONTRIBUTING.MD)


## Copyright & License

See [LICENCE](LICENCE)