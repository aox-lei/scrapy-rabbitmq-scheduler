# -*- coding: utf-8 -*-
import pika


def get_channel(connection, queue_name, durable=True, confirm_delivery=True, is_delay=False):
    """ Init method to return a prepared channel for consuming
    """
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=durable, arguments={
        'x-max-priority': 255
    })
    if confirm_delivery:
        channel.confirm_delivery()

    if is_delay is True:
        exchange_name = "{}-delay".format(queue_name)
        channel.exchange_declare(exchange_name,
                                 exchange_type="x-delayed-message",
                                 arguments={"x-delayed-type": "direct"})
        channel.queue_bind(
            queue=queue_name, exchange=exchange_name, routing_key=queue_name)
    return channel


def connect(connection_url):
    """ Create and return a fresh connection
    """
    return pika.BlockingConnection(pika.URLParameters(connection_url))
