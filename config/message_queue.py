import pika
import json


from config.settings import Settings

params = pika.URLParameters(Settings().RABBITMQ_URI)
connection = pika.BlockingConnection(parameters=params)
channel = connection.channel()


def publish_to_rabbitmq(file_id: str):
    try:
        message = {"video_fid": file_id, "mp3_fid": None}
        channel.queue_declare(queue="rabbitmq", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="rabbitmq",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        print(f"RabbitMQ publish failed: {e}")
