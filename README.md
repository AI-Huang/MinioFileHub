# MinioFileHub 后端项目

一个完整的 **MySQL + MinIO 文件上传与管理系统**，基于 FastAPI 构建，是针对 MySQL Service、MinIO Service 和 FastAPI 的模板工程（Template Project）。

## 项目结构

```
MinIO_Pipeline/
├── app/
│   ├── api/
│   │   ├── v1/                # API 版本 1
│   │   │   ├── schemas/       # Pydantic 模型（API 数据结构）
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file.py    # 文件相关的请求/响应模型
│   │   │   │   └── download_stats.py
│   │   │   ├── __init__.py
│   │   │   ├── files.py       # 文件管理接口
│   │   │   └── auth.py        # JWT 认证接口
│   │   └── __init__.py
│   ├── services/
│   │   ├── mysql/             # MySQL 相关服务
│   │   │   ├── models/        # SQLAlchemy 模型（数据库表结构）
│   │   │   │   └── minio_objects.py
│   │   │   └── mysql_service.py  # MySQL 数据库操作服务
│   │   ├── __init__.py
│   │   └── minio_service.py   # MinIO 对象存储服务
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # 环境配置管理
│   └── __init__.py
├── main.py                    # 应用入口
├── requirements.txt           # Python 依赖清单
├── .env.dev                   # 开发环境配置
├── .env.example               # 环境变量示例
└── README.md                  # 项目说明
```

## 核心功能

| API 端点 | HTTP 方法 | 功能描述 |
|---------|-----------|---------|
| `/files/upload` | POST | 上传文件到 MinIO |
| `/files/{file_id}` | GET | 获取文件详细信息 |
| `/files/{file_id}` | PUT | 更新文件元数据 |
| `/files/{file_id}/download` | GET | 下载文件 |
| `/files/{file_id}/presigned-url` | GET | 获取预签名下载链接 |
| `/files/{file_id}` | DELETE | 删除文件（MinIO + MySQL） |
| `/files/user/{user_id}` | GET | 获取指定用户的文件列表 |
| `/files/` | GET | 分页列出文件（支持用户筛选） |
| `/files/search` | GET | 搜索文件 |
| `/auth/login` | POST | 用户登录（JWT） |
| `/auth/me` | GET | 获取当前用户信息 |
| `/health` | GET | 健康检查 |

## 技术栈

- **Python 3.12+** - 编程语言
- **FastAPI** - 高性能 Web 框架
- **MySQL** - 关系型数据库（存储文件元数据）
- **MinIO** - 对象存储服务（存储实际文件）
- **SQLAlchemy** - ORM 框架
- **Pydantic** - 数据验证与序列化
- **JWT** - 身份认证
- **python-dotenv** - 环境变量管理

## 快速开始

### 1. 环境准备

确保已安装并运行：

- MySQL 服务（默认端口：3306）
- MinIO 服务（默认端口：9000）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env.dev
# 编辑 .env.dev 文件，填写 MySQL 和 MinIO 配置
```

### 4. 启动应用

```bash
python main.py
```

### 5. 访问 API 文档

启动后访问自动生成的 Swagger 文档：

```
http://localhost:8000/docs
```

## 环境变量配置

| 变量名 | 描述 | 默认值 |
|-------|------|-------|
| APP_NAME | 应用名称 | MinIO_Pipeline |
| DEBUG | 调试模式 | False |
| MYSQL_DATABASE_URL | MySQL 连接字符串 | mysql://admin:password@localhost:3306/example_db |
| MINIO_ENDPOINT | MinIO 服务地址 | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO 访问密钥 | minioadmin |
| MINIO_SECRET_KEY | MinIO 密钥 | minioadmin |
| MINIO_BUCKET_NAME | MinIO 存储桶名 | mybucket |
| MINIO_SECURE | 是否使用 HTTPS | False |
| SECRET_KEY | JWT 签名密钥 | your-secret-key |
| ALGORITHM | JWT 算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 令牌过期时间（分钟） | 30 |

## 数据库表结构

### minio_objects 表

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | BIGINT | 主键 ID |
| user_id | BIGINT | 上传用户 ID |
| bucket_name | VARCHAR(255) | 存储桶名称 |
| obj_key | VARCHAR(1024) | 对象路径/文件名 |
| etag | VARCHAR(128) | 文件 ETag/MD5 指纹 |
| size | BIGINT | 文件大小（字节） |
| content_type | VARCHAR(255) | MIME 类型 |
| last_modified | DATETIME | 最后修改时间 |
| version_id | VARCHAR(128) | 版本 ID |
| storage_class | VARCHAR(64) | 存储类型 |
| create_time | DATETIME | 记录创建时间 |
| update_time | DATETIME | 记录更新时间 |

## 使用示例

### 上传文件

```bash
curl -X POST "http://localhost:8000/files/upload" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@your_file.pdf"
```

### 获取文件列表

```bash
curl -X GET "http://localhost:8000/files/?page=1&page_size=20" -H "accept: application/json"
```

### 下载文件

```bash
curl -X GET "http://localhost:8000/files/1/download" -o output_file.pdf
```

## 设计特点

1. **分层架构**：API 层、服务层、数据层分离
2. **版本化 API**：支持多版本 API 管理
3. **对象存储**：文件存储在 MinIO，元数据存储在 MySQL
4. **预签名 URL**：支持生成临时下载链接
5. **分页查询**：支持大量文件的分页浏览
6. **用户隔离**：文件按用户 ID 进行隔离管理
7. **自动建表**：启动时自动创建数据库表结构
