from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: int
    filename: str
    object_name: str
    message: str


class FileResponse(BaseModel):
    id: int
    bucket_name: str
    obj_key: str
    etag: str
    size: int
    content_type: str
    last_modified: Optional[datetime]
    version_id: str
    storage_class: str
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    id: int
    obj_key: str
    size: int
    content_type: str
    create_time: datetime

    class Config:
        from_attributes = True


class FileUpdateRequest(BaseModel):
    user_metadata: Optional[str] = None
    tags: Optional[str] = None
