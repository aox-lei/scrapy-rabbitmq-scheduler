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
SCHEDULER = "scrapy_rabbitmq_scheduler.scheduler.Saas"

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

## TODO
- [ ] 支持延时请求
- [ ] 增加任务持久化配置
- [ ] item队列增加判断数量上限
