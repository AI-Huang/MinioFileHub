# MinIO Pipeline 后端项目

一个基于 Python 的后端服务，集成 MinIO 对象存储和 MySQL 数据库，用于处理文件上传、存储和管理。

## 项目结构

```
MinIO_Pipeline/
├── app/
│   ├── api/            # API 路由
│   │   ├── __init__.py
│   │   ├── files.py     # 文件相关接口
│   │   └── auth.py      # 认证相关接口
│   ├── services/       # 业务逻辑
│   │   ├── __init__.py
│   │   ├── minio_service.py  # MinIO 服务
│   │   └── db_service.py     # 数据库服务
│   ├── models/         # 数据模型
│   │   ├── __init__.py
│   │   └── file.py     # 文件模型
│   ├── schemas/        # 数据验证
│   │   ├── __init__.py
│   │   └── file.py     # 文件相关模式
│   ├── config/         # 配置
│   │   ├── __init__.py
│   │   └── settings.py # 配置项
│   └── __init__.py
├── main.py             # 应用入口
├── requirements.txt    # 依赖
├── .env.example        # 环境变量示例
└── README.md           # 项目说明
```

## 功能特性

- 文件上传到 MinIO
- 文件下载和预览
- 文件元数据管理（存储在 MySQL）
- 文件下载次数统计（存储在 Postgres）
- 用户认证
- API 接口

## 技术栈

- Python 3.9+
- FastAPI
- MinIO SDK
- SQLAlchemy
- MySQL
- Postgres
- Pydantic
- Python-dotenv

## 快速开始

1. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量

   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写相关配置
   ```

3. 启动应用

   ```bash
   python main.py
   ```

4. 访问 API 文档

   ```
   http://localhost:8000/docs
   ```

## 环境变量配置

| 变量名 | 描述 | 默认值 |
|-------|------|-------|
| MYSQL_DATABASE_URL | MySQL 数据库连接字符串 | mysql://admin:password@localhost:3306/example_db |
| POSTGRES_DATABASE_URL | Postgres 数据库连接字符串 | postgresql://admin:password@localhost:5432/example_db |
| MINIO_ENDPOINT | MinIO 服务端点 | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO 访问密钥 | minioadmin |
| MINIO_SECRET_KEY | MinIO 密钥 | minioadmin |
| MINIO_BUCKET_NAME | MinIO 存储桶名称 | mybucket |
| SECRET_KEY | JWT 密钥 | your-secret-key |
| ALGORITHM | JWT 算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 访问令牌过期时间（分钟） | 30
