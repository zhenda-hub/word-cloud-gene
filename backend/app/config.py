from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis配置
    REDIS_URL: str = "redis://redis:6379/0"  # 使用 Docker Compose 中的服务名作为主机名
    
    # 文件上传配置
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

settings = Settings()
