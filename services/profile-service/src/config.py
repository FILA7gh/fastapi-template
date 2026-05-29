from os import environ as env
from typing import List

from pydantic import BaseModel, Field, field_validator


class PostgresConfig(BaseModel):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    login: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    database: str = Field(alias="POSTGRES_DB")


class JWTConfig(BaseModel):
    public_key: str = Field(alias="JWT_PUBLIC_KEY")
    algorithm: str = "RS256"
    issuer: str = "auth-service"
    audience: str = "api"


class RedisConfig(BaseModel):
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")
    redis_db: int = Field(alias="REDIS_DB")


class LoggingConfig(BaseModel):
    level: str = Field("INFO", alias="LOG_LEVEL")


class AppConfig(BaseModel):
    debug: bool = Field(False, alias="DEBUG")
    project_name: str = Field("PROJECT_NAME", alias="PROJECT_NAME")
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["*"], alias="ALLOWED_HOSTS"
    )

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v


class CORSConfig(BaseModel):
    allow_origins: List[str] = Field(
        default_factory=lambda: ["*"], alias="CORS_ALLOW_ORIGINS"
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v


class MediaConfig(BaseModel):
    aws_s3_access_key: str = Field(alias="AWS_S3_ACCESS_KEY")
    aws_s3_secret_key: str = Field(alias="AWS_S3_SECRET_KEY")

    aws_s3_region_name: str = Field(alias="AWS_S3_REGION_NAME")
    aws_s3_bucket_name: str = Field(alias="AWS_S3_BUCKET_NAME")
    aws_s3_media_upload_dir: str = Field(alias="AWS_S3_MEDIA_UPLOAD_DIR")
    aws_s3_endpoint_url: str = Field(alias="AWS_S3_ENDPOINT_URL")
    aws_s3_public_base_url: str = Field(alias="AWS_S3_PUBLIC_BASE_URL")


class RabbitMQConfig(BaseModel):
    host: str = Field(alias="RABBITMQ_HOST")
    port: int = Field(alias="RABBITMQ_PORT")
    login: str = Field(alias="RABBITMQ_USER")
    password: str = Field(alias="RABBITMQ_PASS")


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
    jwt: JWTConfig = Field(default_factory=lambda: JWTConfig(**env))
    redis: RedisConfig = Field(default_factory=lambda: RedisConfig(**env))
    logging: LoggingConfig = Field(default_factory=lambda: LoggingConfig(**env))
    app: AppConfig = Field(default_factory=lambda: AppConfig(**env))
    cors: CORSConfig = Field(default_factory=lambda: CORSConfig(**env))
    media: MediaConfig = Field(default_factory=lambda: MediaConfig(**env))
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig(**env))


config = Config()
