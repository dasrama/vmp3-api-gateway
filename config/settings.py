from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    RABBITMQ_URI: str
    BUCKET_NAME: str = 'vmp3'

    class Config:
        env_file = ".env"
