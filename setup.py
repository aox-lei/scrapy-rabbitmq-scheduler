# -*- coding: utf-8-*-
from setuptools import setup, find_packages
setup(
    name='scrapy-rabbitmq-ds',
    version='1.0.0',
    author='aox.lei',
    author_email='2387813033@qq.com',
    url=''
    description='rabbitmq版本的scrapy分布式爬虫',
    py_modules=['scrapy_rabbitmq'],
    keywords='scrapy scrapy-rabbitmq',
    install_requires=['pika'],
)