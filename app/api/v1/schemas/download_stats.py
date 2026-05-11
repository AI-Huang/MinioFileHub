from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DownloadStats(Base):
    __tablename__ = "download_stats"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False, index=True)
    download_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
