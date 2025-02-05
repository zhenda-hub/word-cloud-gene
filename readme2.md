# 词云图生成器 - 任务管理系统设计

## 数据模型设计

### 1. 任务模型 (WordCloudTask) 


python
class WordCloudTask(BaseModel):
id: str # 任务ID
filename: str # 原始文件名
status: str # 任务状态：PENDING/PROGRESS/SUCCESS/FAILURE
progress: int # 任务进度：0-100
result_path: Optional[str] # 结果文件路径
error_message: Optional[str] # 错误信息
created_at: datetime # 创建时间
updated_at: datetime # 更新时间
retries: int # 重试次数
plaintext
GET /api/tasks
功能：获取任务列表
参数：
page: int # 页码
page_size: int # 每页数量
status: str # 可选，过滤状态
返回：任务列表和分页信息
GET /api/tasks/{task_id}
功能：获取单个任务详情
返回：任务详细信息
DELETE /api/tasks/{task_id}
功能：删除任务
返回：操作结果
POST /api/tasks/{task_id}/retry
功能：重试失败的任务
返回：新的任务ID
GET /api/tasks/statistics
功能：获取任务统计信息
返回：各状态任务数量统计


## 前端组件设计

### 1. 任务列表组件 (TaskList.vue)
- 表格展示任务列表
- 支持分页和状态筛选
- 每行显示：
  - 任务ID（短格式）
  - 原始文件名
  - 创建时间
  - 状态标签
  - 进度条
  - 结果预览（缩略图）
  - 操作按钮（下载、重试、删除）

### 2. 任务统计组件 (TaskStatistics.vue)
- 展示任务总数
- 各状态任务数量
- 成功/失败比率
- 平均处理时间

### 3. 任务详情组件 (TaskDetail.vue)
- 完整任务信息
- 大图预览
- 处理历史
- 错误详情（如果失败）

## 实现细节

### 1. 后端实现
- 使用 Redis 存储任务状态和进度
- 使用文件系统存储生成的图片
- 实现任务清理机制（定期清理老数据）
- 添加任务重试限制和超时处理

### 2. 前端实现
- 使用 Element Plus 的 Table 组件实现列表
- 图片预览使用 el-image 组件
- 使用 Pinia 管理任务状态
- WebSocket 实现实时进度更新

### 3. 任务状态流转


### 4. 性能优化
- 图片懒加载
- 分页加载任务列表
- 缓存任务状态
- 使用缩略图预览

## 开发步骤

### 1. 数据层
- 设计数据模型
- 实现数据存储接口
- 添加数据迁移脚本

### 2. 后端接口
- 实现基础 CRUD 接口
- 添加任务管理功能
- 实现实时进度推送

### 3. 前端组件
- 实现任务列表组件
- 添加任务操作功能
- 实现实时更新

### 4. 系统集成
- 接口联调
- 性能测试
- 错误处理

## 注意事项

### 1. 安全性
- 任务访问权限控制
- 文件清理机制
- 防止资源耗尽

### 2. 可靠性
- 任务重试机制
- 错误恢复
- 数据备份

### 3. 性能
- 并发任务限制
- 资源使用监控
- 大文件处理优化





TODO:

- [x] 添加停用词配置
- [x] 多celery
- [x] 异步进度如何获取
- [x] 多后端, 多前端, 多redis, 多数据库
- [x] redis存了什么
- [x] 预览 背景混乱
- [x] 页面无状态, 怎么保持状态?


改为使用 Element Plus提供的响应式属性



Swagger UI (交互式文档)： http://localhost:8000/docs

