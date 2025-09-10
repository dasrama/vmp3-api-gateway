from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_URI: str
    BUCKET_NAME: str = 'vmp3'
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    REGION_NAME: str
    VIDEO_QUEUE: str = "VIDEO_QUEUE"
    MONGO_URI: str
    
    class Config:
        env_file = ".env"
