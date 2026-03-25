from fastapi import FastAPI, Form

from app.api import auth, files
from app.config.settings import settings
from app.services.db_service import init_db

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME, description="MinIO Pipeline 后端服务", version="1.0.0"
)

# 注册路由
app.include_router(files.router)
app.include_router(auth.router)


# 启动事件
@app.on_event("startup")
def startup_event():
    # 初始化数据库
    init_db()
    print("数据库初始化完成")


# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to MinIO Pipeline API"}


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 上传文件接口（通过文件路径）
@app.post("/upload-by-path")
async def upload_file_by_path(file_path: str = Form(...)):
    """通过文件路径上传文件"""
    import os

    from sqlalchemy.orm import Session

    from app.services.db_service import FileDBService, get_mysql_db
    from app.services.minio_service import minio_service

    # 验证文件是否存在
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}

    # 验证是否是文件
    if not os.path.isfile(file_path):
        return {"error": "路径不是文件"}

    try:
        # 打开文件
        with open(file_path, "rb") as f:
            # 构建文件对象
            import mimetypes

            class FileObj:
                def __init__(self, file_path):
                    self.filename = os.path.basename(file_path)
                    self.file = open(file_path, "rb")
                    self.size = os.path.getsize(file_path)
                    # 使用系统方式读取文件的 MIME 类型
                    content_type, _ = mimetypes.guess_type(file_path)
                    self.content_type = (
                        content_type or "application/octet-stream"
                    )  # 如果无法检测到，使用默认值

            file_obj = FileObj(file_path)

            # 上传到 MinIO
            object_info = minio_service.upload_file(
                file_obj,
                obj_key=os.path.relpath(file_path, os.path.expanduser("~")),
            )

            # 保存文件元数据到数据库
            db: Session = next(get_mysql_db())
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
                "user_metadata": None,
                "tags": None,
                "is_encrypted": 0,
                "retention_mode": "",
                "legal_hold": 0,
            }
            db_file = FileDBService.create_file(db, file_data)

            # 关闭文件
            file_obj.file.close()

            return {
                "id": db_file.id,
                "filename": file_obj.filename,
                "object_name": db_file.obj_key,
                "message": "文件上传成功",
                "file_path": file_path,
            }
    except Exception as e:
        return {"error": f"文件上传失败: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
