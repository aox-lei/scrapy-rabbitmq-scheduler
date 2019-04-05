# -*- coding: utf-8 -*-

import pika

def get_channel(connection, queue_name):
    """ Init method to return a prepared channel for consuming
    """
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.confirm_delivery()

    return channel

def connect(connection_url):
    """ Create and return a fresh connection
    """
    return pika.BlockingConnection(pika.URLParameters(connection_url))
