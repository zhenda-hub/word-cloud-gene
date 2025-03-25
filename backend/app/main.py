from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .celery_app import celery_app
from .config import settings
import os
from celery.result import AsyncResult
from celery.app.control import Inspect
from pathlib import Path
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# 设置文件大小限制为 1GB
MAX_FILE_SIZE = 1024 * 1024 * 1024

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(..., max_length=MAX_FILE_SIZE),
    stop_words: str = Form(default="")
):
    try:
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # 为文件名添加时间戳
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # 格式：年月日时分秒
        file_stem = Path(file.filename).stem
        file_suffix = Path(file.filename).suffix
        timestamped_filename = f"{file_stem}_{timestamp}{file_suffix}"
        
        # 保存文件
        file_path = os.path.join(settings.UPLOAD_FOLDER, timestamped_filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # 创建词云生成任务
        # 处理停用词，以逗号分隔
        custom_stop_words = [w.strip() for w in stop_words.split(',') if w.strip()]
        
        task = celery_app.send_task(
            "generate_wordcloud",
            args=[file_path],
            kwargs={"custom_stop_words": custom_stop_words}
        )
        
        return {"task_id": task.id, "filename": timestamped_filename}  # 返回带时间戳的文件名
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'FAILURE':
        return {"status": "FAILURE", "error": str(task.result)}
    elif task.state == 'SUCCESS':
        return {"status": "SUCCESS", "result": task.result}
    elif task.state == 'PROGRESS':
        return {
            "status": "PROGRESS",
            "result": None,
            "progress": task.info.get('progress', 0),
            "step": task.info.get('step', '')
        }
    return {"status": task.state, "result": None, "progress": 0}

@app.get("/api/tasks/inspect")
async def inspect_tasks():
    i = celery_app.control.inspect()
    
    return {
        "active": i.active(),  # 正在执行的任务
        "reserved": i.reserved(),  # 已被预定但还未执行的任务
        "scheduled": i.scheduled(),  # 计划执行的任务
        "registered": i.registered(),  # 已注册的任务类型
    }

@app.get("/api/tasks/all")
async def get_all_tasks():
    # 获取所有任务ID（从Redis中）
    tasks = []
    try:
        redis_client = celery_app.backend.client
        task_keys = redis_client.keys('celery-task-meta-*')
        
        for key in task_keys:
            task_id = key.decode('utf-8').replace('celery-task-meta-', '')
            result = AsyncResult(task_id, app=celery_app)
            tasks.append({
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "date_done": result.date_done
            })
    except Exception as e:
        return {"error": str(e)}
        
    return tasks 

@app.get("/api/redis/info")
async def get_redis_info():
    try:
        redis_client = celery_app.backend.client
        return {
            "keys": {
                key.decode(): redis_client.type(key).decode()
                for key in redis_client.keys("*")
            },
            "tasks": {
                key.decode().replace("celery-task-meta-", ""): redis_client.get(key).decode()
                for key in redis_client.keys("celery-task-meta-*")
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        # 从 Redis 中删除任务状态
        redis_client = celery_app.backend.client
        task_key = f'celery-task-meta-{task_id}'
        redis_client.delete(task_key)
        
        # 如果有对应的词云图文件，也需要删除
        task_result = celery_app.AsyncResult(task_id)
        if task_result.result and 'image_path' in task_result.result:
            image_path = os.path.join(settings.UPLOAD_FOLDER, task_result.result['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        return {"status": "success", "message": "Task deleted"}
    except Exception as e:
        return {"status": "error", "error": str(e)}