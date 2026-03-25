# MySQL 数据库配置
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

# from app.schemas.download_stats import Base as PostgresBase
# from app.schemas.download_stats import DownloadStats
from app.schemas.minio_objects import Base as MySQLBase
from app.schemas.minio_objects import MinioObject

pymysql.install_as_MySQLdb()
mysql_engine = create_engine(settings.MYSQL_DATABASE_URL)
mysql_session_local = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

# Postgres 数据库配置
# postgres_engine = create_engine(settings.POSTGRES_DATABASE_URL)
# postgres_session_local = sessionmaker(
#     autocommit=False, autoflush=False, bind=postgres_engine
# )


# 依赖项，用于获取 MySQL 数据库会话
def get_mysql_db():
    db = mysql_session_local()
    try:
        yield db
    finally:
        db.close()


# 依赖项，用于获取 Postgres 数据库会话
# def get_postgres_db():
#     db = postgres_session_local()
#     try:
#         yield db
#     finally:
#         db.close()


# 初始化数据库
def init_db():
    # 初始化 MySQL 数据库
    MySQLBase.metadata.create_all(bind=mysql_engine)
    # 初始化 Postgres 数据库
    # PostgresBase.metadata.create_all(bind=postgres_engine)


# MySQL 文件相关的数据库操作
class FileDBService:
    @staticmethod
    def create_file(db, file_data):
        db_file = MinioObject(**file_data)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    @staticmethod
    def get_file_by_id(db, file_id):
        return db.query(MinioObject).filter(MinioObject.id == file_id).first()

    @staticmethod
    def get_files_by_user(db, user_id):
        return db.query(MinioObject).filter(MinioObject.user_id == user_id).all()

    @staticmethod
    def delete_file(db, file_id):
        db_file = db.query(MinioObject).filter(MinioObject.id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False


# Postgres 下载统计相关的数据库操作
# class DownloadStatsService:
#     @staticmethod
#     def increment_download_count(db, file_id):
#         # 查找是否已有记录
#         stats = db.query(DownloadStats).filter(DownloadStats.file_id == file_id).first()
#         if stats:
#             # 更新下载次数
#             stats.download_count += 1
#         else:
#             # 创建新记录
#             stats = DownloadStats(file_id=file_id, download_count=1)
#             db.add(stats)
#         db.commit()
#         db.refresh(stats)
#         return stats

#     @staticmethod
#     def get_download_stats(db, file_id):
#         return db.query(DownloadStats).filter(DownloadStats.file_id == file_id).first()

#     @staticmethod
#     def get_all_download_stats(db):
#         return db.query(DownloadStats).all()
