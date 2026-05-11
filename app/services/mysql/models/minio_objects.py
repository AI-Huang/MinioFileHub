from sqlalchemy import BIGINT, DATETIME, TEXT, VARCHAR, Column
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MinioObject(Base):
    """
    MinIO 对象元数据表
    对应 MySQL 表 minio_object
    """

    __tablename__ = "minio_objects"

    # 主键
    id = Column(BIGINT, primary_key=True, autoincrement=True, comment="主键ID")

    # 用户关联
    user_id = Column(BIGINT, default=0, comment="上传用户ID")

    # 核心信息
    bucket_name = Column(VARCHAR(255), nullable=False, comment="存储桶名称")
    obj_key = Column(VARCHAR(1024), nullable=False, comment="对象路径/文件名（Key）")
    etag = Column(VARCHAR(128), nullable=False, comment="文件ETag/MD5指纹")
    size = Column(BIGINT, nullable=False, comment="对象大小（字节）")
    content_type = Column(VARCHAR(255), default="", comment="MIME类型")

    # 时间（毫秒级）
    last_modified = Column(DATETIME(3), nullable=True, comment="最后修改时间")

    # 版本控制
    version_id = Column(VARCHAR(128), default="", comment="版本ID")
    is_delete_marker = Column(TINYINT(1), default=0, comment="是否删除标记 0=否 1=是")

    # 存储与所有者
    storage_class = Column(VARCHAR(64), default="STANDARD", comment="存储类型")
    owner_id = Column(VARCHAR(255), default="", comment="所有者ID")
    owner_name = Column(VARCHAR(255), default="", comment="所有者名称")

    # 扩展信息（JSON 字符串存储）
    user_metadata = Column(TEXT, nullable=True, comment="用户自定义元数据 JSON")
    tags = Column(TEXT, nullable=True, comment="对象标签 JSON")

    # 安全与合规
    is_encrypted = Column(TINYINT(1), default=0, comment="是否服务端加密")
    retention_mode = Column(VARCHAR(64), default="", comment="保留策略")
    legal_hold = Column(TINYINT(1), default=0, comment="合法持有锁定")

    # 系统时间
    create_time = Column(DATETIME(3), default=func.now(3), comment="记录创建时间")
    update_time = Column(
        DATETIME(3), default=func.now(3), onupdate=func.now(3), comment="记录更新时间"
    )
