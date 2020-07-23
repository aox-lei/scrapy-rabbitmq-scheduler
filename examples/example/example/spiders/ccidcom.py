# -*- coding: utf-8 -*-
import scrapy
from scrapy_rabbitmq_scheduler.spiders import RabbitSpider
from example.items import ArticleItem


class CcidcomSpider(RabbitSpider):
    name = 'ccidcom'
    allowed_domains = ['ccidcom.com']
    # 队列名称
    queue_name = 'ccidcom'
    # 是否是延迟队列
    is_delay_queue = True
    # item队列名称
    items_key = 'item_ccidcom'

    def start_requests(self):
        yield scrapy.Request('http://www.ccidcom.com/', callback=self.parse, meta={'_delay_time': 0})

    def parse(self, response):
        navigation_list = response.css(
            '#nav > div.nav-main.clearfix > ul > li > div > a::attr("href")')
        for _index, _link in enumerate(navigation_list):
            yield response.follow(_link,
                                  dont_filter=True,
                                  callback=self.parse_list, meta={'_delay_time': 0})

    def parse_list(self, response):
        article_list = response.css('div.article-item')
        for info in article_list:
            item = ArticleItem()
            item['title'] = info.css('div.title a>font::text').get()
            item['url'] = info.css('div.title a::attr("href")').get()
            yield item

        yield scrapy.Request('http://www.ccidcom.com/', callback=self.parse, meta={'_delay_time': 0})
