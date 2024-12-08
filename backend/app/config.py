from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 从环境变量获取的配置
    REDIS_URL: str  # 移除默认值，强制从环境变量获取

    # 硬编码的配置
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # model_config = {
    #     'env_file': '.env',
    #     'env_file_encoding': 'utf-8'
    # }

settings = Settings()
