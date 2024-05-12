from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_hours: int
    aws_access_key_id: str
    aws_secret_access_key_id: str
    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings=Settings()

s3 = boto3.client('s3', aws_access_key_id=settings.aws_access_key_id, aws_secret_access_key=settings.aws_secret_access_key_id, config=boto3.session.Config(signature_version='s3v4'), region_name='eu-north-1')
