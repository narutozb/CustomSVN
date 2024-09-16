# client_base.py
import logging

import requests
from datetime import datetime
from typing import Any, Optional
from config import Config  # 导入配置文件

logger = logging.getLogger(__name__)


class ClientBase:
    def __init__(self):
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.refresh_threshold = Config.REFRESH_THRESHOLD  # 从配置读取刷新阈值
        self.base_url = Config.API_URL  # 从配置读取 API 基础路径
        self.username = Config.USERNAME  # 从配置读取用户名
        self.password = Config.PASSWORD  # 从配置读取密码
        self.login()

    def login(self):
        logger.info("尝试登录...")
        url = f'{self.base_url}user/login/'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self.session.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
            # 获取令牌的过期时间
            access_token_expiration = data.get('access_token_expiration')
            self.token_expiry = datetime.utcfromtimestamp(access_token_expiration)
            self.session.headers.update(self.headers)
            logger.info(f"登录成功，访问令牌将于 {self.token_expiry} 过期。")
        else:
            logger.error(f"登录失败，状态码：{response.status_code}，响应内容：{response.text}")
            raise Exception('登录失败')

    def refresh_access_token(self):
        logger.info("尝试刷新访问令牌...")
        url = f'{self.base_url}user/token/refresh/'
        response = self.session.post(url, json={
            'refresh': self.refresh_token
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            # 获取新的令牌过期时间
            access_token_expiration = data.get('access_token_expiration')
            self.token_expiry = datetime.utcfromtimestamp(access_token_expiration)
            self.session.headers.update(self.headers)
            logger.info(f"访问令牌刷新成功，新令牌将于 {self.token_expiry} 过期。")
        elif response.status_code == 401:
            logger.warning("刷新令牌已过期，尝试重新登录...")
            try:
                self.login()
            except Exception as e:
                logger.error("重新登录失败，请检查您的凭据。")
                raise
        else:
            logger.error(f"刷新令牌失败，状态码：{response.status_code}，响应：{response.text}")
            raise Exception('刷新令牌失败')

    @property
    def headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def ensure_token_valid(self):
        current_time = datetime.utcnow()
        time_diff = (self.token_expiry - current_time).total_seconds()
        logger.warning(f"当前时间：{current_time}，令牌过期时间：{self.token_expiry}，剩余有效期：{time_diff} 秒")
        # 如果令牌将在 refresh_threshold 秒内过期，刷新令牌
        if time_diff < self.refresh_threshold:
            self.refresh_access_token()

    def make_request(self, method, url, **kwargs):
        self.ensure_token_valid()
        full_url = f'{self.base_url}{url}'
        response = self.session.request(method, full_url, **kwargs)
        # 如果返回401，尝试刷新令牌并重试
        if response.status_code == 401:
            logger.warning("访问令牌可能已过期，尝试刷新...")
            self.refresh_access_token()
            self.session.headers.update(self.headers)
            response = self.session.request(method, full_url, **kwargs)
        return response

    def get_api(self, api_class: Any):
        return api_class(self)
