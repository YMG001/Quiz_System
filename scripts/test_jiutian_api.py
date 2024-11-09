import os
import sys
import json
import time
import jwt
import asyncio
import aiohttp
from typing import Dict, Any

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.utils.logger import LoggerManager

logger = LoggerManager().get_logger(__name__)

class JiutianAPITester:
    def __init__(self):
        # 九天模型配置
        self.api_key = "**apikey**"
        self.base_url = "https://jiutian.10086.cn/largemodel/api/v1"
        self.model = "jiutian-qianwen"  # 修改为九天千问模型
        
    def generate_token(self, exp_seconds: int = 3600) -> str:
        """生成九天平台的 token"""
        try:
            api_id, secret = self.api_key.split(".")
            
            payload = {
                "api_key": api_id,
                "exp": int(round(time.time())) + exp_seconds,
                "timestamp": int(round(time.time())),
            }

            token = jwt.encode(
                payload,
                secret,
                algorithm="HS256",
                headers={"alg": "HS256", "typ": "JWT", "sign_type": "SIGN"},
            )
            
            logger.info("成功生成九天平台token")
            return token
            
        except Exception as e:
            logger.error(f"生成token失败: {str(e)}")
            raise
            
    async def test_completion(self) -> None:
        """测试补全接口"""
        try:
            token = self.generate_token()
            
            request_data = {
                "modelId": self.model,
                "prompt": "你是什么大模型？",
                "params": {
                    "temperature": 0.8,
                    "top_p": 0.95
                },
                "history": [],
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Apifox/1.0.0 (https://apifox.com)"
            }
            
            logger.info("开始测试九天模型API...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/completions",
                    json=request_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    logger.info(f"响应状态码: {response.status}")
                    logger.debug(f"原始响应: {response_text}")
                    
                    if response.status == 200:
                        try:
                            # 处理响应文本，移除 "data:" 前缀
                            if response_text.startswith('data:'):
                                response_text = response_text[5:]
                            
                            json_response = json.loads(response_text)
                            logger.info("成功解析响应")
                            logger.debug(f"解析后的响应: {json.dumps(json_response, ensure_ascii=False, indent=2)}")
                            
                            if 'response' in json_response:
                                content = json_response['response']
                                logger.info(f"模型回复内容: {content}")
                            elif 'code' in json_response:
                                logger.error(f"API返回错误: {json_response.get('message', '未知错误')}")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败: {str(e)}")
                    else:
                        logger.error(f"请求失败，状态码: {response.status}")
                        
        except Exception as e:
            logger.error(f"测试过程中出错: {str(e)}", exc_info=True)

    async def test_qa_generation(self) -> None:
        """测试生成问答对"""
        try:
            token = self.generate_token()
            
            request_data = {
                "modelId": self.model,
                "prompt": """请根据以下内容生成3个问答对：
                
                Python是一种高级编程语言，以其简洁的语法和强大的生态系统而闻名。
                
                请按照以下格式返回：
                问题1：xxx
                答案1：xxx
                
                问题2：xxx
                答案2：xxx""",
                "params": {
                    "temperature": 0.8,
                    "top_p": 0.95
                },
                "history": [],
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Apifox/1.0.0 (https://apifox.com)"
            }
            
            logger.info("开始测试问答对生成...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/completions",
                    json=request_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    logger.info(f"响应状态码: {response.status}")
                    logger.debug(f"原始响应: {response_text}")
                    
                    if response.status == 200:
                        try:
                            # 处理响应文本，移除 "data:" 前缀
                            if response_text.startswith('data:'):
                                response_text = response_text[5:]
                            
                            json_response = json.loads(response_text)
                            if 'response' in json_response:
                                logger.info(f"生成的问答对：\n{json_response['response']}")
                                
                                # 解析生成的问答对
                                qa_text = json_response['response']
                                logger.info("\n解析后的问答对：")
                                current_qa = {}
                                for line in qa_text.split('\n'):
                                    line = line.strip()
                                    if line.startswith('问题'):
                                        if current_qa:
                                            logger.info(f"Q: {current_qa.get('question')}")
                                            logger.info(f"A: {current_qa.get('answer')}\n")
                                        current_qa = {'question': line.split('：', 1)[1] if '：' in line else line}
                                    elif line.startswith('答案') and current_qa:
                                        current_qa['answer'] = line.split('：', 1)[1] if '：' in line else line
                                
                                # 打印最后一个问答对
                                if current_qa:
                                    logger.info(f"Q: {current_qa.get('question')}")
                                    logger.info(f"A: {current_qa.get('answer')}")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败: {str(e)}")
                    else:
                        logger.error(f"请求失败，状态码: {response.status}")
                        
        except Exception as e:
            logger.error(f"测试问答生成失败: {str(e)}", exc_info=True)

async def main():
    tester = JiutianAPITester()
    # 先测试基本的补全接口
    await tester.test_completion()
    logger.info("\n" + "="*50 + "\n")
    # 再测试问答对生成
    await tester.test_qa_generation()

if __name__ == "__main__":
    asyncio.run(main())