import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare("test-x", exchange_type="x-delayed-message",
                         arguments={"x-delayed-type": "direct"})
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_bind(queue="task_queue", exchange="test-x",
                   routing_key="task_queue")
channel.basic_publish(
    exchange='test-x',
    routing_key='task_queue',
    body='Hello World! Delayed',
    properties=pika.BasicProperties(headers={"x-delay": 10000})
)
print(" [x] Sent 'Hello World! Delayed'")
connection.close()
