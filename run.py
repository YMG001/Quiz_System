from app import create_app
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = create_app()

if __name__ == "__main__":
    # 启用调试模式和自动重载
    app.run(
        debug=True,  # 启用调试模式
        use_reloader=True,  # 启用自动重载
        host='0.0.0.0',  # 允许外部访问
        port=5000
    ) 