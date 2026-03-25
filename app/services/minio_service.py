import os
import uuid

from minio import Minio
from minio.error import S3Error

from app.config.settings import settings


class MinioService:
    def __init__(self):
        # 初始化 MinIO 客户端
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        # 确保存储桶存在
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        """确保存储桶存在，如果不存在则创建"""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file, obj_key=None, user_id=None):
        """上传文件到 MinIO

        Args:
            file: 文件对象
            obj_key: 对象键，如果为 None 则自动生成
            user_id: 用户 ID，用于构建路径

        Returns:
            dict: 上传后的对象信息，包含元数据
        """
        if obj_key is None:
            # 生成唯一的对象键
            import datetime

            file_extension = os.path.splitext(file.filename)[1]
            # 构建路径：年/月/日/用户ID/文件名
            today = datetime.datetime.now()
            date_path = f"{today.year}/{today.month:02d}/{today.day:02d}"
            user_path = f"user_{user_id}" if user_id else "anonymous"
            unique_name = f"{uuid.uuid4()}{file_extension}"
            obj_key = f"{date_path}/{user_path}/{unique_name}"

        # 上传文件
        self.client.put_object(
            self.bucket_name,
            obj_key,
            file.file,
            file.size,
            content_type=file.content_type,
        )

        # 获取上传后的对象信息
        try:
            # 获取对象元数据
            stat = self.client.stat_object(self.bucket_name, obj_key)

            # 构建返回的对象信息
            object_info = {
                "bucket_name": self.bucket_name,
                "obj_key": obj_key,
                "etag": stat.etag,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "version_id": stat.version_id or "",
                "is_delete_marker": int(stat.is_delete_marker),
                "storage_class": stat.storage_class,
                "owner_id": stat.owner.id if stat.owner else "",
                "owner_name": stat.owner.name if stat.owner else "",
            }
            return object_info
        except Exception as e:
            # 如果获取元数据失败，返回基本信息
            return {
                "bucket_name": self.bucket_name,
                "obj_key": obj_key,
                "etag": "",
                "size": file.size,
                "content_type": file.content_type,
                "last_modified": None,
                "version_id": "",
                "is_delete_marker": 0,
                "storage_class": "STANDARD",
                "owner_id": "",
                "owner_name": "",
            }

    def get_file(self, obj_key):
        """获取文件

        Args:
            obj_key: 对象键

        Returns:
            bytes: 文件内容
        """
        try:
            response = self.client.get_object(self.bucket_name, obj_key)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise e

    def delete_file(self, obj_key):
        """删除文件

        Args:
            obj_key: 对象键
        """
        try:
            self.client.remove_object(self.bucket_name, obj_key)
            return True
        except S3Error as e:
            raise e

    def get_presigned_url(self, obj_key, expires=3600):
        """获取预签名 URL

        Args:
            obj_key: 对象键
            expires: 过期时间（秒）

        Returns:
            str: 预签名 URL
        """
        try:
            url = self.client.presigned_get_object(self.bucket_name, obj_key, expires)
            return url
        except S3Error as e:
            raise e


# 创建 MinIO 服务实例
minio_service = MinioService()
