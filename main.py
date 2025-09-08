import aiofiles
from bson import ObjectId
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from config.settings import Settings
from config.message_queue import publish_to_rabbitmq


app = FastAPI()

video_client = AsyncIOMotorClient(Settings().MONGO_URI)
video_db = video_client["video"]
fs_video = AsyncIOMotorGridFSBucket(video_db)

mp3_client = AsyncIOMotorClient(Settings().MONGO_URI)
mp3_db = video_client["mp3"]
fs_mp3 = AsyncIOMotorGridFSBucket(mp3_db)


async def upload_file_to_gridfs(file: UploadFile):
    # Open an async GridFS upload stream
    upload_stream =fs_video.open_upload_stream(file.filename)
    print("async chunk by chunk read")

    # Read the file asynchronously in chunks
    async for chunk in file_chunks(file, chunk_size=1024 * 1024):
        await upload_stream.write(chunk)   # non-blocking write

    await upload_stream.close()
    print("upload stream closed")
    return upload_stream._id


async def file_chunks(file: UploadFile, chunk_size: int = 1024 * 1024):
    """Yield file chunks asynchronously"""
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        yield chunk


@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # open upload stream (GridFS writer)
        print("file goes to upload")
        

        file_id = await upload_file_to_gridfs(file)
        print("file_id : ", file_id)
        # publish to RabbitMQ in background
        background_tasks.add_task(publish_to_rabbitmq, str(file_id))

        return JSONResponse(
            status_code=200,
            content={"message": "success", "data": str(file_id), "error": None},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal server error",
                "data": None,
                "error": str(e),
            },
        )


@app.get("/download")
async def download_mp3(file_id: str):
    try:
        file_object_id = ObjectId(file_id)

        grid_out = await fs_mp3.open_download_stream(file_id=file_object_id)

        async def file_iterator():
            while True:
                chunk = await grid_out.readchunk()
                if not chunk:
                    break
                yield chunk

        headers = {"Content-Disposition": f"attachment; filename={file_id}.mp3"}
        return StreamingResponse(file_iterator(), media_type="audio/mpeg", headers=headers)

    except Exception as e:  
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal server error",
                "data": None,
                "error": str(e)
            }
        )
      