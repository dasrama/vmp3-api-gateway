import boto3
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from config.settings import Settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=Settings().AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Settings().AWS_SECRET_ACCESS_KEY,
    region_name=Settings().REGION_NAME
)

async def upload_to_s3(file: UploadFile, object_name=None):
    if object_name is None:
        object_name=file.filename

    content = await file.read()

    s3_client.put_object(
        bucket=Settings().BUCKET_NAME,
        key=object_name,
        body=content
    )

    return object_name


async def download_from_s3(bucket_name: str, object_name: str):
    response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
    file_stream = response["Body"]

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachemnt; filename={object_name}"}
    )
