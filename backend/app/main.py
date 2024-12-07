from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .celery_app import celery_app
from .config import settings
import os

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
        task = celery_app.send_task("generate_wordcloud", args=[file_path])
        
        return {"task_id": task.id, "filename": file.filename}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    return {"status": task.status, "result": task.result} 