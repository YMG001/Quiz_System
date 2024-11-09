import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # 数据库配置
    DB_USERNAME = os.getenv("DB_USERNAME", "quiz_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "quzi123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "quiz_system")
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 应用配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

    def __init__(self):
        # 验证必要的环境变量
        if not all([self.DB_USERNAME, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME]):
            raise ValueError("Missing required database configuration")
        if not self.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")

settings = Settings() 