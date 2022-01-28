import os

import pika

RABBIT_MQ_HOST = os.getenv("RABBITMQ_HOST") or 'localhost'


async def publish_message(msg):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='rm_file_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='rm_file_queue',
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ))

    connection.close()
