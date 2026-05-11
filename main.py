from fastapi import FastAPI

from app.api.v1 import auth, files
from app.config.settings import settings
from app.services.mysql.mysql_service import init_db

app = FastAPI(
    title=settings.APP_NAME, description="MinIO Pipeline 后端服务", version="1.0.0"
)

app.include_router(files.router)
app.include_router(auth.router)


@app.on_event("startup")
def startup_event():
    init_db()
    print("数据库初始化完成")


@app.get("/")
async def root():
    return {"message": "Welcome to MinIO Pipeline API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
