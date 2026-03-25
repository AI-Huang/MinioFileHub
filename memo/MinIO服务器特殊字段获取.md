# MinIO 服务器特殊字段获取

## 特殊字段说明

在当前的 MinIO 上传实现中，以下字段使用了默认值，没有从 MinIO 服务器获取实际值：

1. **is_encrypted**：设置为 0，表示默认未加密
2. **retention_mode**：设置为空字符串，表示默认无保留策略
3. **legal_hold**：设置为 0，表示默认无合法持有锁定

## 获取方法

这些字段在 MinIO 中属于高级功能，需要通过特定的 API 调用来获取：

- **is_encrypted**：MinIO 服务器端加密状态，需要通过 `get_object_lock_configuration` 或类似 API 获取
- **retention_mode**：对象保留策略，需要通过 `get_object_retention` API 获取
- **legal_hold**：合法持有锁定状态，需要通过 `get_object_legal_hold` API 获取

## 实现建议

当前的实现中，我们只获取了 MinIO 对象的基本元数据，没有调用这些高级 API。如果需要获取这些字段的值，需要在 `MinioService.upload_file` 方法中添加相应的 API 调用。

### 代码示例

```python
# 获取对象锁定配置
try:
    lock_config = self.client.get_object_lock_configuration(self.bucket_name, obj_key)
    # 处理锁定配置
    is_encrypted = 1 if lock_config else 0
except Exception as e:
    is_encrypted = 0

# 获取对象保留策略
try:
    retention = self.client.get_object_retention(self.bucket_name, obj_key)
    retention_mode = retention.mode
except Exception as e:
    retention_mode = ""

# 获取合法持有锁定状态
try:
    legal_hold = self.client.get_object_legal_hold(self.bucket_name, obj_key)
    legal_hold = 1 if legal_hold.status == "ON" else 0
except Exception as e:
    legal_hold = 0
```

## 注意事项

- 这些 API 调用可能会增加上传过程的时间，因为需要额外的网络请求
- 部分功能可能需要在 MinIO 服务器上启用相应的配置
- 对于大多数常规使用场景，使用默认值已经足够
