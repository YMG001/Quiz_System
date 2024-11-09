import os
from werkzeug.utils import secure_filename
from typing import List, Tuple
from app.utils.logger import log_operation, LoggerManager
logger = LoggerManager().get_logger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

class FileService:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder

    @log_operation("检查文件类型")
    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @log_operation("保存文件")
    def save_file(self, file) -> Tuple[bool, str]:
        if not file or not file.filename:
            return False, "没有选择文件"
            
        if not self.allowed_file(file.filename):
            return False, "文件格式不支持"
            
        try:
            # 确保上传目录存在
            os.makedirs(self.upload_folder, exist_ok=True)
            
            # 安全地处理文件名并保留原始扩展名
            filename = secure_filename(file.filename)
            # 确保文件名中包含扩展名
            if '.' not in filename:
                original_ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{filename}.{original_ext}"
            
            # 构建完整的文件路径
            file_path = os.path.join(self.upload_folder, filename)
            
            # 保存文件
            file.save(file_path)
            
            return True, file_path
            
        except Exception as e:
            return False, f"文件保存失败: {str(e)}"

    @log_operation("提取文本")
    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        logger.info(f"文件路径: {file_path}")
        
        try:
            # 获取文件扩展名
            _, extension = os.path.splitext(file_path)
            
            if not extension:
                # 尝试从原始文件名获取扩展名
                raise ValueError("文件必须包含扩展名(.txt, .pdf, 或 .docx)")
                
            # 移除扩展名开头的点号并转换为小写
            extension = extension[1:].lower()
            
            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError(f"不支持的文件类型: {extension}")
                
            if extension == 'txt':
                return self._extract_from_txt(file_path)
            elif extension == 'pdf':
                return self._extract_from_pdf(file_path)
            elif extension == 'docx':
                return self._extract_from_docx(file_path)
                
        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}")
            raise

    @log_operation("提取TXT文本")
    def _extract_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                    return content
            except UnicodeDecodeError:
                raise ValueError("无法读取文件编码")

    @log_operation("提取PDF文本")
    def _extract_from_pdf(self, file_path: str) -> str:
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"PDF解析失败: {str(e)}")

    @log_operation("提取DOCX文本")
    def _extract_from_docx(self, file_path: str) -> str:
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Word文档解析失败: {str(e)}")