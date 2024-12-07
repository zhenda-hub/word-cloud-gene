from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .celery_app import celery_app
from .config import settings
import os
from celery.result import AsyncResult
from celery.app.control import Inspect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # 创建词云生成任务
        task = celery_app.send_task("generate_wordcloud", args=[file_path], kwargs={})
        
        return {"task_id": task.id, "filename": file.filename}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'FAILURE':
        return {"status": "FAILURE", "error": str(task.result)}
    elif task.state == 'SUCCESS':
        return {"status": "SUCCESS", "result": task.result}
    return {"status": task.state, "result": None}

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