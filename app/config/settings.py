import os

from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # 默认为dev

# 加载.env文件
env_file = f".env.{ENVIRONMENT}"
try:
    load_dotenv(env_file)
except FileNotFoundError:
    raise FileNotFoundError(f"警告：未找到环境配置文件 {env_file}")


class Settings:

    APP_NAME = os.getenv("APP_NAME")

    # MySQL 数据库配置
    MYSQL_DATABASE_URL = os.getenv("MYSQL_DATABASE_URL")

    # MinIO 配置
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False") == "True"


settings = Settings()
