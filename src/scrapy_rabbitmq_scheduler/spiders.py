# -*- coding: utf-8 -*-
import scrapy
import pickle
from scrapy.utils.reqser import request_from_dict


class RabbitSpider(scrapy.Spider):
    def _make_request(self, mframe, hframe, body):
        try:
            request = request_from_dict(pickle.loads(body), self)
        except Exception as e:
            body = body.decode()
            request = scrapy.Request(body, callback=self.parse, dont_filter=True)
        return request
