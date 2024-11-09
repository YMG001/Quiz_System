#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    ：backtrader学习 
@File       ：九天_api_key.py
@IDE        ：PyCharm 
@Author     ：ymg
@Date       ：2024/10/30 16:35 
@description：
"""

import time
import jwt

def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
    "api_key": id,
    "exp": int(round(time.time())) + exp_seconds,
    "timestamp": int(round(time.time())),
    }

    return jwt.encode(
    payload,
    secret,
    algorithm="HS256",
    headers={"alg": "HS256", "typ": "JWT", "sign_type": "SIGN"},
    )

apiKey="**key**"
# Token有效期为3600秒（1小时）
jwt_token = generate_token(apiKey, 3600)
print(jwt_token)