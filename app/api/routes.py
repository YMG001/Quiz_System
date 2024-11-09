from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from app.services.file_service import FileService
from app.services.llm_service import LLMService
from app.services.quiz_service import QuizService
from app.services.auth_service import AuthService
from app.utils.decorators import login_required
from app.models.qa_pair import QAPair
from app.database.db import db
from app.utils.logger import LoggerManager, log_operation
from app.config.settings import settings
import asyncio
import os

# 获取logger
logger = LoggerManager().get_logger(__name__)

api = Blueprint('api', __name__)
file_service = FileService('uploads')
quiz_service = QuizService()
auth_service = AuthService()

@api.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        success, message = auth_service.register(
            request.form['username'],
            request.form['email'],
            request.form['password']
        )
        if success:
            flash(message, 'success')
            return redirect(url_for('api.login'))
        flash(message, 'error')
    return render_template('auth/register.html')

@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        success, message = auth_service.login(
            request.form['username'],
            request.form['password']
        )
        if success:
            flash(message, 'success')
            return redirect(url_for('api.index'))
        flash(message, 'error')
    return render_template('auth/login.html')

@api.route('/logout')
@login_required
def logout():
    # 清除所有会话数据
    session.clear()
    flash('已成功退出登录', 'success')
    return redirect(url_for('api.login'))

@api.route('/')
@login_required
def index():
    # 获取当前用户的所有题目，不再限制数量
    questions = quiz_service.get_user_questions(session['user_id'])
    return render_template('index.html', questions=questions)

@api.route('/upload', methods=['POST'])
@login_required
@log_operation("文件上传处理")
def upload_file():
    # 获取当前用户信息
    user_id = session.get('user_id')
    username = session.get('username')
    logger.info(f"用户 {username}(ID:{user_id}) 开始上传文件")

    if 'file' not in request.files:
        logger.warning(f"用户 {username} 未选择文件")
        flash("请选择要上传的文件", "error")
        return redirect(url_for('api.index'))
        
    file = request.files['file']
    if not file.filename:
        logger.warning(f"用户 {username} 上传的文件名为空")
        flash("没有选择文件", "error")
        return redirect(url_for('api.index'))
        
    # 记录文件信息
    logger.info(f"文件信息: 名称={file.filename}, 类型={file.content_type}, 大小={len(file.read())}字节")
    file.seek(0)  # 重置文件指针
    
    try:
        # 获取模型选择和相关参数
        model_type = request.form.get('model_type', 'local')
        model_params = {
            'model_type': model_type
        }
        
        # 根据不同的模型类型获取对应的参数
        if model_type == 'local':
            model_params['local_model'] = request.form.get('local_model', 'llama2')
            model_params['use_local'] = True
        elif model_type == 'jiutian':
            model_params.update({
                'use_local': False,
                'use_jiutian': True,
                'jiutian_model': request.form.get('jiutian_model'),
                'jiutian_api_key': request.form.get('jiutian_api_key')
            })
            logger.info(f"使用九天模型: {model_params['jiutian_model']}")
        elif model_type == 'openai':
            model_params.update({
                'use_local': False,
                'api_key': settings.OPENAI_API_KEY
            })
        
        # 保存文件
        logger.info(f"开始保存文件: {file.filename}")
        success, result = file_service.save_file(file)
        
        if not success:
            logger.error(f"文件保存失败: {result}")
            flash(result, "error")
            return redirect(url_for('api.index'))
            
        logger.info(f"文件保存成功: {result}")
        
        # 提取文本
        logger.info("开始提取文本内容")
        content = file_service.extract_text(result)
        logger.info(f"成功提取文本，内容长度: {len(content)} 字符")
        
        # 初始化LLM服务
        llm_service = LLMService(**model_params)
        
        # 生成问答对
        logger.info(f"开始使用{model_type}模型生成问答对")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        qa_pairs = loop.run_until_complete(llm_service.generate_qa_pairs(content))
        loop.close()
        
        if not qa_pairs:
            logger.warning("未生成任何问答对")
            flash("生成问答对失败", "error")
            return redirect(url_for('api.index'))
            
        logger.info(f"成功生成 {len(qa_pairs)} 个问答对")
        
        # 保存到数据库
        logger.info("开始保存问答对到数据库")
        try:
            for qa in qa_pairs:
                qa_pair = QAPair(
                    question=qa['question'],
                    answer=qa['answer'],
                    source_file=file.filename,
                    user_id=user_id
                )
                db.session.add(qa_pair)
            
            db.session.commit()
            logger.info("问答对保存成功")
            
        except Exception as e:
            logger.error(f"保存问答对到数据库失败: {str(e)}")
            db.session.rollback()
            flash("保存问答对失败", "error")
            return redirect(url_for('api.index'))
        
        # 记录文件处理完成
        logger.info(f"用户 {username} 的文件 {file.filename} 处理完成")
        flash("文件上传成功！已生成问答对。", "success")
        return redirect(url_for('api.index'))
        
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}", exc_info=True)
        # 清理临时文件
        if 'result' in locals() and os.path.exists(result):
            try:
                os.remove(result)
                logger.info(f"已清理临时文件: {result}")
            except Exception as cleanup_error:
                logger.error(f"清理临时文件失败: {str(cleanup_error)}")
                
        flash(f"处理文件时出错: {str(e)}", "error")
        return redirect(url_for('api.index'))

@api.route('/quiz', methods=['GET'])
def get_quiz():
    count = request.args.get('count', 10, type=int)
    questions = quiz_service.get_random_questions(count)
    return jsonify({"questions": questions})

@api.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    result = quiz_service.check_answer(
        data.get('question_id'),
        data.get('answer')
    )
    return jsonify(result) 