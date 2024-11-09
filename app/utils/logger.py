import logging
import os
import functools
from logging.handlers import RotatingFileHandler
from typing import Optional, Callable
from datetime import datetime

class LoggerManager:
    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._init_log_dir()
        return cls._instance

    def _init_log_dir(self):
        self.log_dir = 'logs'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            # 如果没有指定日志文件，使用模块名作为文件名
            if log_file is None:
                log_file = f"{name}.log"

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_format)

            # 文件处理器
            file_handler = RotatingFileHandler(
                os.path.join(self.log_dir, log_file),
                maxBytes=10*1024*1024,
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            self._loggers[name] = logger

        return self._loggers[name]

def log_operation(operation_name: Optional[str] = None):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取logger
            logger = LoggerManager().get_logger(func.__module__)
            
            # 获取操作名称
            op_name = operation_name or func.__name__
            
            # 记录开始时间
            start_time = datetime.now()
            logger.info(f"开始执行 {op_name}")
            
            try:
                # 记录参数
                logger.debug(f"参数: args={args}, kwargs={kwargs}")
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"{op_name} 执行成功，耗时: {execution_time:.2f}秒")
                
                return result
                
            except Exception as e:
                # 记录异常信息
                logger.error(f"{op_name} 执行失败: {str(e)}", exc_info=True)
                raise
                
        return wrapper
    return decorator 