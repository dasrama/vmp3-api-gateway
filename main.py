from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId

from config.settings import Settings

app = FastAPI()


video_client = AsyncIOMotorClient(Settings().MONGO_URI)
video_db = video_client["video"]
fs_video = AsyncIOMotorGridFSBucket(video_db)

mp3_client = AsyncIOMotorClient(Settings().MONGO_URI)
mp3_db = video_client["mp3"]
fs_mp3 = AsyncIOMotorGridFSBucket(mp3_db)


@app.post("upload")
async def upload_video(file: UploadFile = File(...)):
    try: 
        contents = await file.read()

        file_id = await fs_video.upload_from_stream(
            file.filename,
            contents
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "success",
                "data": str(file_id),
                "error": None
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal server error",
                "data": None,
                "error": str(e)
            }
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
      