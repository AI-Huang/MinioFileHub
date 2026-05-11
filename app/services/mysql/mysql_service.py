import pymysql
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.services.mysql.models.minio_objects import Base as MySQLBase
from app.services.mysql.models.minio_objects import MinioObject

pymysql.install_as_MySQLdb()
mysql_engine = create_engine(settings.MYSQL_DATABASE_URL)
mysql_session_local = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)


def get_mysql_db():
    db = mysql_session_local()
    try:
        yield db
    finally:
        db.close()


def init_db():
    MySQLBase.metadata.create_all(bind=mysql_engine)


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
    def update_file(db, file_id, update_data):
        db_file = db.query(MinioObject).filter(MinioObject.id == file_id).first()
        if db_file:
            for key, value in update_data.items():
                setattr(db_file, key, value)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_file(db, file_id):
        db_file = db.query(MinioObject).filter(MinioObject.id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False

    @staticmethod
    def list_files(db, page=1, page_size=20, user_id=None):
        query = db.query(MinioObject)
        if user_id is not None:
            query = query.filter(MinioObject.user_id == user_id)
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size).all()

    @staticmethod
    def search_files(db, keyword, user_id=None):
        query = db.query(MinioObject).filter(
            or_(
                MinioObject.obj_key.like(f"%{keyword}%"),
                MinioObject.etag.like(f"%{keyword}%"),
            )
        )
        if user_id is not None:
            query = query.filter(MinioObject.user_id == user_id)
        return query.all()
