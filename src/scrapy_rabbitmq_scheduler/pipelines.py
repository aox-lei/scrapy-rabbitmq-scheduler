from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from . import connection

default_serialize = ScrapyJSONEncoder().encode


class RabbitmqPipeline(object):
    def __init__(self, item_key, connection_url):
        self.server = connection.connect(connection_url)
        self.item_key = item_key
        self.serialize = default_serialize
        self.channel = connection.get_channel(self.server, self.item_key)

    @classmethod
    def from_crawler(cls, crawler):
        if hasattr(crawler.spider, 'items_key'):
            item_key = crawler.spider.items_key
        else:
            item_key = 'items_{spider_name}'.format(
                spider_name=crawler.spider.name)
        return cls(item_key=item_key,
                   connection_url=crawler.settings.get(
                       'RABBITMQ_CONNECTION_PARAMETERS'))

    def process_item(self, item, spider):
        data = self.serialize(item)

        self.channel.basic_publish(exchange='',
                                   routing_key=self.item_key,
                                   body=data)
        return item

    def close(self):
        """Close channel"""
        logger.error('pipeline channel is closed!!!!!!!!!!!')
        self.channel.close()
