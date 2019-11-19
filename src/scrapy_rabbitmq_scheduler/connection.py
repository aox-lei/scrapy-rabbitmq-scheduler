# -*- coding: utf-8 -*-
import pika


def get_channel(connection, queue_name, durable=True, confirm_delivery=True):
    """ Init method to return a prepared channel for consuming
    """
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=durable, arguments={
        'x-max-priority':255
    })
    if confirm_delivery:
        channel.confirm_delivery()

    return channel


def connect(connection_url):
    """ Create and return a fresh connection
    """
    return pika.BlockingConnection(pika.URLParameters(connection_url))
