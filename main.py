from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

from utils.message_queue import publish_to_rabbitmq
from config.settings import Settings
from utils.s3_helper import upload_to_s3, download_from_s3


app = FastAPI()

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # open upload stream (GridFS writer)
        print("file goes to upload")
        

        file_name = await upload_to_s3(file)

        background_tasks.add_task(publish_to_rabbitmq, file_name)

        return JSONResponse(
            status_code=200,
            content={"message": "success", "data": file_name, "error": None},
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
def download_video(filename: str):
    try:
        return download_from_s3(Settings().BUCKET_NAME, filename)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "internal server error", "data": None, "error": str(e)},
        )
    