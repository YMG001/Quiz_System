from flask import session
from app.models.user import User
from app.database.db import db

class AuthService:
    @staticmethod
    def register(username, email, password):
        if User.query.filter_by(username=username).first():
            return False, "用户名已存在"
            
        if User.query.filter_by(email=email).first():
            return False, "邮箱已被注册"
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return True, "注册成功"
    
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return True, "登录成功"
            
        return False, "用户名或密码错误"
    
    @staticmethod
    def logout():
        # 清除所有会话数据
        session.clear()
        return True, "已成功退出登录"
        
    @staticmethod
    def get_current_user():
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None