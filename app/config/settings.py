import os

from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

env_file = f".env.{ENVIRONMENT}"
try:
    load_dotenv(env_file)
except FileNotFoundError:
    raise FileNotFoundError(f"警告：未找到环境配置文件 {env_file}")


class Settings:
    APP_NAME = os.getenv("APP_NAME", "MinIO Pipeline")
    DEBUG = os.getenv("DEBUG", "False") == "True"

    MYSQL_DATABASE_URL = os.getenv("MYSQL_DATABASE_URL")

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False") == "True"

    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


settings = Settings()
