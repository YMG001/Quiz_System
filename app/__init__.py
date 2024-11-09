from flask import Flask
from config import Config
from app.database.db import init_db
from app.api.routes import api
import logging
import os
import pymysql
from app.utils.logger import LoggerManager

# 获取logger
logger = LoggerManager().get_logger(__name__)

# 注册 PyMySQL 作为 MySQLdb
pymysql.install_as_MySQLdb()

def create_app():
    logger.info("Creating Flask application...")
    try:
        app = Flask(__name__, 
                   template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
        app.config.from_object(Config)
        
        # 确保上传文件夹存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 初始化数据库
        logger.info("Initializing database...")
        init_db(app)
        
        # 注册蓝图
        logger.info("Registering blueprints...")
        app.register_blueprint(api)
        
        logger.info("Application created successfully!")
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise