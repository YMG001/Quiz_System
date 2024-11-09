import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app
from app.models.qa_pair import QAPair
from app.database.db import db

def add_test_data():
    app = create_app()
    
    with app.app_context():
        # 添加测试数据
        test_pairs = [
            QAPair(
                question="什么是Python?",
                answer="Python是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。",
                source_file="test.txt"
            ),
            QAPair(
                question="Flask是什么?",
                answer="Flask是一个轻量级的Python Web框架，具有高度的灵活性和可扩展性。",
                source_file="test.txt"
            )
        ]
        
        for pair in test_pairs:
            db.session.add(pair)
        
        db.session.commit()
        print("测试数据添加成功！")

if __name__ == "__main__":
    add_test_data() 