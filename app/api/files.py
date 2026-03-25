import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.schemas.file import FileResponse, FileUploadResponse
from app.services.db_service import (  # DownloadStatsService,; get_postgres_db,
    FileDBService,
    get_mysql_db,
)
from app.services.minio_service import minio_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = 1,  # 实际应用中应该从认证中获取
    db: Session = Depends(get_mysql_db),
):
    """上传文件"""
    try:
        # 上传到 MinIO
        object_info = minio_service.upload_file(file)

        # 构建文件路径
        file_path = f"/{object_info['obj_key']}"

        # 保存文件元数据到数据库
        file_data = {
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
            "user_metadata": None,  # 可以根据需要添加自定义元数据
            "tags": None,  # 可以根据需要添加标签
            "is_encrypted": 0,  # 默认未加密
            "retention_mode": "",  # 默认无保留策略
            "legal_hold": 0,  # 默认无合法持有锁定
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


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    mysql_db: Session = Depends(get_mysql_db),
):
    """下载文件"""
    db_file = FileDBService.get_file_by_id(mysql_db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        # 从 MinIO 获取文件
        file_data = minio_service.get_file(db_file.obj_key)

        # 返回文件
        from fastapi.responses import Response

        return Response(
            content=file_data,
            media_type=db_file.content_type,
            headers={"Content-Disposition": f"attachment; filename={db_file.filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_mysql_db)):
    """删除文件"""
    db_file = FileDBService.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        # 从 MinIO 删除文件
        minio_service.delete_file(db_file.obj_key)

        # 从数据库删除文件记录
        FileDBService.delete_file(db, file_id)

        return {"message": "文件删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_files(user_id: int, db: Session = Depends(get_mysql_db)):
    """获取用户的所有文件"""
    files = FileDBService.get_files_by_user(db, user_id)
    return files


# @router.get("/{file_id}/stats")
# async def get_file_download_stats(file_id: int, db: Session = Depends(get_postgres_db)):
#     """获取文件下载统计"""
#     stats = DownloadStatsService.get_download_stats(db, file_id)
#     if not stats:
#         return {"file_id": file_id, "download_count": 0}
#     return {"file_id": file_id, "download_count": stats.download_count}


# @router.get("/stats/all")
# async def get_all_download_stats(db: Session = Depends(get_postgres_db)):
#     """获取所有文件的下载统计"""
#     stats_list = DownloadStatsService.get_all_download_stats(db)
#     return [
#         {"file_id": stats.file_id, "download_count": stats.download_count}
#         for stats in stats_list
#     ]
