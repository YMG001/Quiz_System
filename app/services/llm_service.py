from typing import List, Dict, Optional
import json
import time
import jwt
import aiohttp
from app.utils.logger import LoggerManager, log_operation

logger = LoggerManager().get_logger(__name__)

class LLMService:
    def __init__(self, model_type: str, **kwargs):
        """
        初始化LLM服务
        
        Args:
            model_type: 模型类型 (local/jiutian/openai)
            **kwargs: 其他参数
                - use_local: 是否使用本地模型
                - local_model: 本地模型名称
                - use_jiutian: 是否使用九天模型
                - jiutian_model: 九天模型名称
                - jiutian_api_key: 九天平台API Key
                - api_key: OpenAI API Key
        """
        self.model_type = model_type
        
        if model_type == 'local':
            self.use_local = True
            self.local_model = kwargs.get('local_model', 'llama2')
            self.local_api_url = "http://localhost:11434/api/generate"
            
        elif model_type == 'jiutian':
            self.use_jiutian = True
            self.jiutian_model = kwargs.get('jiutian_model')
            self.jiutian_api_key = kwargs.get('jiutian_api_key')
            self.jiutian_base_url = "https://jiutian.10086.cn/largemodel/api/v1"
            # 生成九天平台的token
            self.jiutian_token = self._generate_jiutian_token()
            
        else:  # openai
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=kwargs.get('api_key'))
            
    def _generate_jiutian_token(self, exp_seconds: int = 3600) -> str:
        """
        生成九天平台的token
        
        Args:
            exp_seconds: token有效期（秒），默认1小时
            
        Returns:
            str: 生成的token
        """
        try:
            api_id, secret = self.jiutian_api_key.split(".")
            
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
            logger.error(f"生成九天平台token失败: {str(e)}")
            raise Exception("生成token失败，请检查API Key格式是否正确")
            
    @log_operation("生成问答对")
    async def generate_qa_pairs(self, content: str) -> List[Dict]:
        """根据不同的模型类型调用相应的生成方法"""
        try:
            if self.model_type == 'local':
                return await self._generate_local(content)
            elif self.model_type == 'jiutian':
                return await self._generate_jiutian(content)
            else:
                return await self._generate_openai(content)
        except Exception as e:
            logger.error(f"生成问答对失败: {str(e)}")
            return self._generate_fallback_qa_pairs(content)

    async def _generate_jiutian(self, content: str) -> List[Dict]:
        """使用九天大模型生成问答对"""
        try:
            # 构建提示词，完全匹配测试文件的格式
            prompt = f"""请根据以下内容生成5个问答对：

{content}

请按照以下格式返回：
问题1：xxx
答案1：xxx

问题2：xxx
答案2：xxx"""
            
            # 构建请求数据，完全匹配测试文件的格式
            request_data = {
                "modelId": self.jiutian_model,
                "prompt": prompt,
                "params": {  # 添加 params 字段
                    "temperature": 0.8,
                    "top_p": 0.95
                },
                "history": [],
                "stream": False
            }
            
            # 设置请求头，确保包含所有必要的头部
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.jiutian_token}",
                "User-Agent": "Apifox/1.0.0 (https://apifox.com)"  # 添加 User-Agent
            }
            
            logger.info(f"开始请求九天模型，请求地址：{self.jiutian_base_url}/completions")
            logger.debug(f"请求头：{headers}")
            logger.debug(f"请求数据：{json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.jiutian_base_url}/completions",
                    json=request_data,
                    headers=headers,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"九天模型原始响应: {response_text}")
                    
                    if response.status == 200:
                        try:
                            # 处理响应文本，移除 "data:" 前缀
                            if response_text.startswith('data:'):
                                response_text = response_text[5:]
                                
                            json_response = json.loads(response_text)
                            
                            # 检查错误码
                            if json_response.get('code') == 500:
                                logger.error(f"九天模型返回错误: {json_response.get('message')}")
                                return self._generate_fallback_qa_pairs(content)
                                
                            # 获取模型的回复内容
                            if 'response' in json_response:
                                model_response = json_response['response']
                                logger.info(f"成功获取模型回复：{model_response}")
                                
                                # 解析文本格式的响应
                                qa_pairs = []
                                current_qa = {}
                                
                                # 按行解析问答对
                                for line in model_response.split('\n'):
                                    line = line.strip()
                                    if not line:
                                        continue
                                        
                                    if line.startswith('问题'):
                                        # 如果已有未保存的问答对，先保存
                                        if current_qa.get('question') and current_qa.get('answer'):
                                            qa_pairs.append(current_qa)
                                            current_qa = {}
                                        
                                        current_qa['question'] = line.split('：', 1)[1] if '：' in line else line
                                    elif line.startswith('答案') and current_qa.get('question'):
                                        current_qa['answer'] = line.split('：', 1)[1] if '：' in line else line
                                
                                # 保存最后一个问答对
                                if current_qa.get('question') and current_qa.get('answer'):
                                    qa_pairs.append(current_qa)
                                
                                if qa_pairs:
                                    logger.info(f"成功从九天模型生成 {len(qa_pairs)} 个问答对")
                                    return qa_pairs
                                else:
                                    logger.warning("解析九天模型响应失败，未找到有效的问答对")
                                    return self._generate_fallback_qa_pairs(content)
                            else:
                                logger.error("九天模型响应格式不正确")
                                logger.debug(f"完整响应：{json_response}")
                                return self._generate_fallback_qa_pairs(content)
                        except json.JSONDecodeError as e:
                            logger.error(f"解析JSON响应失败: {str(e)}")
                            logger.debug(f"原始响应文本: {response_text}")
                            return self._generate_fallback_qa_pairs(content)
                    else:
                        logger.error(f"九天模型API调用失败，状态码: {response.status}")
                        logger.debug(f"错误响应: {response_text}")
                        return self._generate_fallback_qa_pairs(content)
                    
        except Exception as e:
            logger.error(f"调用九天模型失败: {str(e)}", exc_info=True)
            return self._generate_fallback_qa_pairs(content)
            
    async def _generate_local(self, content: str) -> List[Dict]:
        """使用本地Ollama模型生成问答对"""
        try:
            system_prompt = """
            你是一个专业的教育工作者。请根据提供的内容生成5个问答对。
            你必须以JSON数组格式返回，每个元素包含question和answer字段。
            示例格式：
            [
                {"question": "问题1", "answer": "答案1"},
                {"question": "问题2", "answer": "答案2"}
            ]
            请确保返回的是合法的JSON格式。
            """
            
            prompt = f"{system_prompt}\n\n内容：{content}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.local_api_url,
                    json={
                        "model": self.local_model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', '')
                        
                        # 尝试从响应中提取JSON
                        try:
                            # 查找第一个 '[' 和最后一个 ']' 的位置
                            start = response_text.find('[')
                            end = response_text.rfind(']') + 1
                            if start != -1 and end != 0:
                                json_str = response_text[start:end]
                                qa_pairs = json.loads(json_str)
                                logger.info(f"成功生成 {len(qa_pairs)} 个问答对")
                                return qa_pairs
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON解析失败: {str(e)}")
                            logger.debug(f"原始响应: {response_text}")
                    
                    logger.error("生成问答对失败，使用备用方案")
                    return self._generate_fallback_qa_pairs(content)
                    
        except Exception as e:
            logger.error(f"调用本地模型失败: {str(e)}", exc_info=True)
            return self._generate_fallback_qa_pairs(content)
            
    async def _generate_openai(self, content: str) -> List[Dict]:
        """使用OpenAI API生成问答对"""
        try:
            system_prompt = """
            请根据提供的内容生成5个问答对。返回格式必须是JSON数组，每个元素包含question和answer字段。
            示例格式：
            [
                {"question": "问题1", "answer": "答案1"},
                {"question": "问题2", "answer": "答案2"}
            ]
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ]
            )
            
            result = response.choices[0].message.content
            try:
                qa_pairs = json.loads(result)
                logger.info(f"成功生成 {len(qa_pairs)} 个问答对")
                return qa_pairs
            except json.JSONDecodeError as e:
                logger.error(f"OpenAI响应解析失败: {str(e)}")
                return self._generate_fallback_qa_pairs(content)
                
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}", exc_info=True)
            return self._generate_fallback_qa_pairs(content)
            
    def _generate_fallback_qa_pairs(self, content: str) -> List[Dict]:
        """生成备用问答对"""
        return [
            {
                "question": "无法生成问题，请检查系统配置或重试",
                "answer": "系暂时无法生成答案，请稍后再试"
            }
        ]