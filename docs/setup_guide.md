# Quiz System 项目启动指南

## 1. 环境准备

### 1.1 安装必要工具
- Python 3.10+
- Poetry（依赖管理工具）
- MySQL 数据库

### 1.2 Poetry 安装 

```bash
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
MacOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```



## 2. 项目初始化

### 2.1 创建项目结构

```bash
quiz-system/
├── app/
│ ├── init.py
│ ├── api/
│ │ └── routes.py
│ ├── database/
│ │ └── db.py
│ ├── models/
│ │ └── qa_pair.py
│ ├── services/
│ │ ├── file_service.py
│ │ ├── llm_service.py
│ │ └── quiz_service.py
│ └── templates/
│ └── index.html
├── scripts/
│ ├── init_db.py
│ ├── test_db.py
│ └── add_test_data.py
├── config.py
├── pyproject.toml
└── run.py
```


### 2.2 配置 Poetry
创建 `pyproject.toml`:

```toml
[tool.poetry]
name = "quiz-system"
version = "0.1.0"
description = "A quiz system based on document analysis"
authors = ["Your Name <your.email@example.com>"]
[tool.poetry.dependencies]
python = "^3.10"
flask = "^2.3.0"
flask-sqlalchemy = "^3.0.0"
python-dotenv = "^1.0.0"
openai = "^1.0.0"
werkzeug = "^2.3.0"
PyPDF2 = "^3.0.0"
python-docx = "^0.8.11"
pymysql = "^1.1.0"
```

### 2.3 安装依赖

```bash
poetry install
```

## 3. 数据库配置

### 3.1 创建数据库和用户

```sql
-- 登录 MySQL
mysql -u root -p
-- 创建数据库
CREATE DATABASE quiz_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 创建用户并授权
CREATE USER 'quiz_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON quiz_system. TO 'quiz_user'@'localhost';
FLUSH PRIVILEGES;
```


### 3.2 环境变量配置
创建 `.env` 文件：

```text
DB_USERNAME=quiz_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=quiz_system
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secret_key
FLASK_DEBUG=1
FLASK_ENV=development
```


## 4. 数据库初始化

### 4.1 测试数据库连接
```bash
poetry run python scripts/test_db.py
```


### 4.2 创建数据库表
```bash
poetry run python scripts/init_db.py
```


### 4.3 添加测试数据

```bash
poetry run python scripts/add_test_data.py
```

## 5. 运行应用
```bash
poetry run python run.py
```


访问 `http://localhost:5000` 查看应用。

## 6. 常见问题及解决方案

### 6.1 Poetry 相关问题

#### 问题：找不到 poetry 命令
解决：确保 Poetry 已正确安装并添加到系统路径。

#### 问题：依赖安装失败
解决：使用 `poetry lock --no-update` 后再 `poetry install`

### 6.2 数据库相关问题

#### 问题：Access denied for user
解决：
- 检查数据库用户名和密码是否正确
- 确保用户有正确的数据库权限
- 验证 `.env` 文件中的配置

#### 问题：找不到数据库
解决：确保已创建数据库并正确配置数据库名

### 6.3 应用运行问题

#### 问题：ModuleNotFoundError
解决：确保在正确的虚拟环境中运行，使用 `poetry shell` 或 `poetry run`

#### 问题：找不到模板
解决：检查模板文件路径是否正确，确保在正确的目录结构下

## 7. 开发建议

1. 使用 `poetry shell` 进入虚拟环境进行开发
2. 定期更新依赖 `poetry update`
3. 保持 `.env` 文件的安全性，不要提交到版本控制
4. 遵循项目的目录结构，保持代码组织清晰

## 8. 下一步计划

1. 添加用户认证系统
2. 实现更多文件格式的支持
3. 优化前端界面
4. 添加测试用例
5. 完善错误处理机制
