import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.schemas.file import (
    FileListResponse,
    FileResponse,
    FileUpdateRequest,
    FileUploadResponse,
)
from app.services.minio_service import minio_service
from app.services.mysql.mysql_service import FileDBService, get_mysql_db

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_mysql_db),
):
    """上传文件"""
    try:
        object_info = minio_service.upload_file(file, user_id=user_id)

        file_data = {
            "user_id": user_id,
            "bucket_name": object_info["bucket_name"],
            "obj_key": object_info["obj_key"],
            "etag": object_info["etag"],
            "size": object_info["size"],
            "content_type": object_info["content_type"],
            "last_modified": object_info["last_modified"],
            "version_id": object_info["version_id"],
            "is_delete_marker": object_info["is_delete_marker"],
            "storage_class": object_info["storage_class"],
            "owner_id": object_info["owner_id"],
            "owner_name": object_info["owner_name"],
            "user_metadata": None,
            "tags": None,
            "is_encrypted": 0,
            "retention_mode": "",
            "legal_hold": 0,
        }
        db_file = FileDBService.create_file(db, file_data)

        return FileUploadResponse(
            id=db_file.id,
            filename=file.filename,
            object_name=db_file.obj_key,
            message="文件上传成功",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: Session = Depends(get_mysql_db)):
    """获取文件信息"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")
    return db_file


@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    request: FileUpdateRequest,
    db: Session = Depends(get_mysql_db),
):
    """更新文件元数据"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        update_data = {}
        if request.user_metadata is not None:
            update_data["user_metadata"] = request.user_metadata
        if request.tags is not None:
            update_data["tags"] = request.tags

        if update_data:
            FileDBService.update_file(db, file_id, update_data)
            db.refresh(db_file)

        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件更新失败: {str(e)}")


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_mysql_db),
):
    """下载文件"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        file_data = minio_service.get_file(db_file.obj_key)
        filename = os.path.basename(db_file.obj_key)

        from fastapi.responses import Response

        return Response(
            content=file_data,
            media_type=db_file.content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


@router.get("/{file_id}/presigned-url")
async def get_presigned_url(
    file_id: int,
    expires: int = 3600,
    db: Session = Depends(get_mysql_db),
):
    """获取文件预签名URL"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        url = minio_service.get_presigned_url(db_file.obj_key, expires=expires)
        return {"url": url, "expires_in": expires}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预签名URL失败: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_mysql_db)):
    """删除文件"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        minio_service.delete_file(db_file.obj_key)
        FileDBService.delete_file(db, file_id)
        return {"message": "文件删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")


@router.get("/user/{user_id}", response_model=list[FileListResponse])
async def get_user_files(user_id: int, db: Session = Depends(get_mysql_db)):
    """获取用户的所有文件"""
    files = FileDBService.get_files_by_user(db, user_id)
    return files


@router.get("/", response_model=list[FileListResponse])
async def list_files(
    page: int = 1,
    page_size: int = 20,
    user_id: int = None,
    db: Session = Depends(get_mysql_db),
):
    """列出文件列表（支持分页和用户筛选）"""
    files = FileDBService.list_files(db, page, page_size, user_id)
    return files


@router.get("/search")
async def search_files(
    keyword: str,
    user_id: int = None,
    db: Session = Depends(get_mysql_db),
):
    """搜索文件"""
    files = FileDBService.search_files(db, keyword, user_id)
    return files
