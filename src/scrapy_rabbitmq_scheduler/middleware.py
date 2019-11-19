import pika
import logging

from scrapy.exceptions import IgnoreRequest

logger = logging.getLogger(__name__)


class RabbitMQMiddleware(object):
    """ Middleware used to close message from current queue or
        send unsuccessful messages to be rescheduled.
    """
    def __init__(self, settings):
        self.requeue_list = settings.get('SCHEDULER_REQUEUE_ON_STATUS', [])
        self.init = True

    @classmethod
    def from_settings(self, settings):
        return RabbitMQMiddleware(settings)

    @classmethod
    def from_crawler(self, crawler):
        return RabbitMQMiddleware(crawler.settings)

    def ensure_init(self, spider):
        if self.init:
            self.spider = spider
            self.scheduler = spider.crawler.engine.slot.scheduler
            self.stats = spider.crawler.stats
            self.init = False

    def process_response(self, request, response, spider):
        self.ensure_init(spider)
        if not is_a_picture(response):
            if response.status in self.requeue_list:
                self.requeue(response)
                self.ack(request, response)
                request.meta['requeued'] = True
                raise IgnoreRequest
            else:
                self.ack(request, response)
        else:
            self.process_picture(response)
        return response

    def has_delivery_tag(self, request):
        if self.spider.settings.get('RABBITMQ_CONFIRM_DELIVERY', True) is not True:
            return False
        if 'delivery_tag' not in request.meta:
            logger.error('Request %(request)s does not have a deliver tag.' %
                         {'request': request})
            return False
        return True

    def process_picture(self, response):
        logger.info('Picture (%(status)d): %(url)s', {
            'url': response.url,
            'status': response.status
        })
        self.inc_stat('picture')

    def requeue(self, response):
        self.scheduler.requeue_message(response.url)
        logger.info('Requeued (%(status)d): %(url)s', {
            'url': response.url,
            'status': response.status
        })
        self.inc_stat('requeued')

    def ack(self, request, response):
        if self.has_delivery_tag(request):
            delivery_tag = request.meta.get('delivery_tag')
            self.scheduler.ack_message(delivery_tag)
            logger.info('Acked (%(status)d): %(url)s' % {
                'url': response.url,
                'status': response.status
            })
            self.inc_stat('acked')

    def inc_stat(self, stat):
        self.stats.inc_value('scheduler/acking/%(stat)s/rabbitmq' %
                             {'stat': stat},
                             spider=self.spider)


def is_a_picture(response):
    picture_exts = ['.png', '.jpg']
    return any([response.url.endswith(ext) for ext in picture_exts])
