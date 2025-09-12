# 词云图生成网站

基于 Vue3 + FastAPI + Redis + Celery 的在线词云图生成服务

## 技术架构

- 前端：Vue3 + Element Plus
- 后端：FastAPI
- 任务队列：Celery + Redis
- 文件存储：本地存储/对象存储

## 功能模块

### 前端页面

1. 首页
   - 文件上传组件
   - 词云图配置面板（颜色、形状、字体等）
   - 生成结果展示区域
   - 历史记录列表

2. 历史记录页面
   - 已生成词云图列表
   - 支持下载和删除操作

### 后端 API

1. 文件处理相关

## Docker 部署架构

### 服务组件

1. Frontend (前端服务)
   - 镜像：node:latest
   - 端口：80
   - 服务：Nginx + Vue3 应用

2. Backend (后端服务)
   - 镜像：python:3.9
   - 端口：8000
   - 服务：FastAPI 应用

3. Redis
   - 镜像：redis:latest
   - 端口：6379
   - 用途：消息队列和缓存

4. Celery Worker
   - 镜像：python:3.9
   - 服务：Celery Worker 进程
   - 用途：异步任务处理

### 目录结构