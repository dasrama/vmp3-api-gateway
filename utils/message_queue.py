import pika
import json
from config.settings import Settings


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

def publish_to_rabbitmq(file_id: str):
    try:
        message = {"video_fid": file_id, "bucket":Settings().BUCKET_NAME, "mp3_fid": None}
        channel.queue_declare(queue=Settings().VIDEO_QUEUE, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=Settings().VIDEO_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print(f"Published in RabbitMQ")
    except Exception as e:
        print(f"RabbitMQ publish failed: {e}")
