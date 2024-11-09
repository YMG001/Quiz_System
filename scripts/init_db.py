import os
import sys
import logging

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app
from app.database.db import db
from app.models.user import User
from app.models.qa_pair import QAPair

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    logger.info("Starting database initialization...")
    app = create_app()
    
    with app.app_context():
        # 删除所有现有表
        logger.info("Dropping all existing tables...")
        db.drop_all()
        
        # 创建所有表
        logger.info("Creating new tables...")
        db.create_all()
        
        # 创建测试用户
        logger.info("Creating test user...")
        test_user = User(username='test', email='test@example.com')
        test_user.set_password('test123')
        db.session.add(test_user)
        
        # 创建一些测试问答对
        logger.info("Creating test QA pairs...")
        test_pairs = [
            QAPair(
                question="什么是Python?",
                answer="Python是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。",
                source_file="test.txt",
                user_id=1  # 将属于测试用户
            ),
            QAPair(
                question="Flask是什么?",
                answer="Flask是一个轻量级的Python Web框架，具有高度的灵活性和可扩展性。",
                source_file="test.txt",
                user_id=1  # 将属于测试用户
            )
        ]
        
        for pair in test_pairs:
            db.session.add(pair)
            
        try:
            db.session.commit()
            logger.info("Database initialization completed successfully!")
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database() 