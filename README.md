## Scrapy分布式RabbitMQ调度器
## 安装

使用pip安装

```
pip install scrapy-rabbitmq-scheduler
```
或者克隆这个项目并且执行setup.py安装
```
python setup.py install
```

## 使用
### 第一步: 在你的项目中的settings.py中添加配置项
```
# 指定项目的调度器
SCHEDULER = "scrapy_rabbitmq_scheduler.scheduler.SaaS"

# 指定rabbitmq的连接DSN
RABBITMQ_CONNECTION_PARAMETERS = 'amqp://guest:guest@localhost:5672/'

# 指定重试的http状态码(重新加回队列重试)
SCHEDULER_REQUEUE_ON_STATUS = [500]

# 指定下载器中间件, 确认任务是否成功
DOWNLOADER_MIDDLEWARES = {
    'scrapy_rabbitmq_scheduler.middleware.RabbitMQMiddleware': 999
}
# 指定item处理方式, item会加入到rabbitmq中
ITEM_PIPELINES = {
    'scrapy_rabbitmq_scheduler.pipelines.RabbitmqPipeline': 300,
}
```

### 第二步: 修改Spider的继承类
```
import scrapy
from scrapy_rabbitmq_scheduler.spiders import RabbitSpider

class CustomSpider(RabbitSpider):
    name = 'custom_spider'    
    queue_name = 'test_urls' # 指定任务队列的名称
    items_key = 'test_item' # 指定item队列名称

    def parse(self, response):
        item = ... # parse item
        yield item
```

### 第三步: 将任务写入到RabbitMQ队列
```
#!/usr/bin/env python
import pika
import settings

connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_CONNECTION_PARAMETERS))
channel = connection.channel()

queue_key = 'test_urls'

# 读取文件中的链接并写入到队列中
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
urls.txt
```text
http://www.baidu.com
```
## 高级特色
### 1. 支持消息优先级
1. 消息优先级的范围为0~255, 数字越大, 优先级越高
```python
yield scrapy.Request(url, priority=优先级)
```
则可以直接指定消息的优先级

### 2. 队列持久化
```python
# settings.py
RABBITMQ_DURABLE = True # 是否持久化队列, True为持久化 False为非持久化, 默认True
```

### 3. 消息确认
```python
# settings.py
RABBITMQ_CONFIRM_DELIVERY = True # 消息是否需要确认, True为需要, False为不需要, 默认是True
```
## TODO
- [ ] 支持延时请求
- [x] 增加任务持久化配置
