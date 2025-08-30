import pika
import json
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorGridFSBucket


async def upload(file: UploadFile, fs: AsyncIOMotorGridFSBucket, channel):
    try:
        contents = await file.read()

        file_id = await fs.upload_from_stream(
            file.filename,
            contents
        )

    except Exception as e:
        fs.delete(file_id)
        return JSONResponse(
            status_code=500,
            content={
                "status": "Internal server error",
                "data": None,
                "error": "500 Internal server error"
            }
        )
    
    message = {
        "video_fid": str(file_id),
        "mp3_fid": None,
    }

    try:
        channel.queue_declare(queue='rabbitmq')

        channel.basic_publish(
            exchange='',
            routing_key='rabbitmq',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

        return file_id
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "Internal server error",
                "data": None,
                "error": str(e)
            }
        )



