import os
import sys
import pymysql
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

load_dotenv()

def test_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USERNAME', 'quiz_user'),
            password=os.getenv('DB_PASSWORD', 'your_password'),
            database=os.getenv('DB_NAME', 'quiz_system')
        )
        print("数据库连接成功！")
        connection.close()
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")

if __name__ == "__main__":
    test_connection() 