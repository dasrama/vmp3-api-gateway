from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    RABBITMQ_URI: str
    BUCKET_NAME: str = 'vmp3'
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    REGION_NAME: str

    class Config:
        env_file = ".env"
