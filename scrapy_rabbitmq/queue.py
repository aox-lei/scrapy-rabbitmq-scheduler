# system packages
import sys
import time
import pika
import logging

# module packages
from . import connection

logger = logging.getLogger(__name__)


class IQueue(object):
    """Per-spider queue/stack base class"""

    def __init__(self):
        """Init method"""
        raise NotImplementedError

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, url):
        """Push an url"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop an url"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        raise NotImplementedError


class RabbitMQQueue(IQueue):
    """Per-spider FIFO queue"""

    def __init__(self, connection_url, key, exchange=None):
        """Initialize per-spider RabbitMQ queue.

        Parameters:
            connection_url -- rabbitmq connection url
            key -- rabbitmq routing key
        """
        self.key = key
        self.connection_url = connection_url
        self.server = None
        self.connect()

    def __len__(self):
        """Return the length of the queue"""
        declared = self.channel.queue_declare(self.key, passive=True)
        return declared.method.message_count

    def _try_operation(function):
        """Wrap unary method by reconnect procedure"""
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < 10:
                try:
                    return function(self, *args, **kwargs)
                except Exception as e:
                    retries += 1
                    msg = 'Function %s failed. Reconnecting... (%d times)' %\
                            (str(function), retries)
                    logger.info(msg)
                    self.connect()
                    time.sleep((retries-1)*5)
            return None
        return wrapper

    @_try_operation
    def pop(self, no_ack=False):
        """Pop a message"""
        return self.channel.basic_get(queue=self.key, auto_ack=no_ack)

    @_try_operation
    def ack(self, delivery_tag):
        """Ack a message"""
        self.channel.basic_ack(delivery_tag=delivery_tag)

    @_try_operation
    def push(self, body, headers=None):
        """Push a message"""
        properties = None
        if  headers:
            properties = pika.BasicProperties(headers=headers)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.key,
            body=body,
            properties=properties
        )

    def connect(self):
        """Make a connection"""
        if self.server:
            try:
                self.server.close()
            except:
                pass
        self.server = connection.connect(self.connection_url)
        self.channel = connection.get_channel(self.server, self.key)

    def close(self):
	    """Close channel"""
	    self.channel.close()

    def clear(self):
        """Clear queue/stack"""
        self.channel.queue_purge(self.key)

__all__ = ['SpiderQueue']
