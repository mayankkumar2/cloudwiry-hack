import os
import uuid
from models import FileMetadata
import pika
import connection.mongo_con as _

DATA_PATH = os.getenv("DATA_PATH") or "data"
RABBIT_MQ_HOST = os.getenv("RABBITMQ_HOST") or 'localhost'

print(RABBIT_MQ_HOST, "<<<<<<<<")
def cleanup(_id: str):
    _path = f"{DATA_PATH}/{_id}"
    if os.path.exists(_path):
        os.remove(_path)


def delete_file(_id: str):
    id = uuid.UUID(_id)
    FileMetadata(file_id=id).delete()
    cleanup(_id)


connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_MQ_HOST))
channel = connection.channel()

channel.queue_declare(queue='rm_file_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    _id = body.decode()
    delete_file(_id)
    print(f" [x] Done cleaning {_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rm_file_queue', on_message_callback=callback)

channel.start_consuming()
