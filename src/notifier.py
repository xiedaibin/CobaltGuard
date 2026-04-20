import requests
import json
import os
import logging
import base64
import hashlib
import hmac
import time
from typing import Optional

logger = logging.getLogger(__name__)

class FeishuNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        self.webhook_secret = os.getenv("FEISHU_WEBHOOK_SECRET")
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        self.access_token = None

    def _gen_sign(self, timestamp: str, secret: str) -> str:
        """生成飞书 Webhook 签名"""
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def _get_access_token(self):
        """
        获取 tenant_access_token 以用于上传图片。
        """
        if not self.app_id or not self.app_secret:
            logger.error("未提供 FEISHU_APP_ID 或 FEISHU_APP_SECRET，无法上传图片。")
            return None
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                self.access_token = data.get("tenant_access_token")
                return self.access_token
            else:
                logger.error(f"获取 Access Token 失败: {data}")
        except Exception as e:
            logger.error(f"获取 Access Token 时出错: {e}")
        return None

    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到飞书并返回 image_key。
        """
        token = self._get_access_token()
        if not token:
            return None
        
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        try:
            with open(image_path, "rb") as f:
                import os
                form_files = {
                    "image_type": (None, "message"),
                    "image": (os.path.basename(image_path), f, "image/png")
                }
                resp = requests.post(url, headers=headers, files=form_files)
                resp.raise_for_status()
                data = resp.json()
                if data.get("code") == 0:
                    return data.get("data", {}).get("image_key")
                else:
                    logger.error(f"图片上传失败: {data}")
        except Exception as e:
            logger.error(f"图片上传时出错: {e}")
        return None

    def send_text(self, text: str):
        """
        通过 Webhook 发送简单文本消息。
        """
        if not self.webhook_url:
            logger.error("未设置 FEISHU_WEBHOOK_URL。")
            return

        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        
        if self.webhook_secret:
            timestamp = str(int(time.time()))
            sign = self._gen_sign(timestamp, self.webhook_secret)
            payload["timestamp"] = timestamp
            payload["sign"] = sign

        try:
            resp = requests.post(self.webhook_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # 检查业务错误码
            code = data.get("code") if data.get("code") is not None else data.get("StatusCode")
            if code == 0:
                logger.info("文本消息已发送至飞书。")
            else:
                msg = data.get("msg") or data.get("StatusMessage") or "未知错误"
                logger.error(f"文本消息下发失败 (业务错误) - 错误码: {code}, 原因: {msg}")
        except Exception as e:
            logger.error(f"发送文本消息时出错: {e}")

    def send_interactive_card(self, title: str, content: str, image_key: Optional[str] = None):
        """
        通过 Webhook 发送交互式卡片。
        """
        if not self.webhook_url:
            logger.error("未设置 FEISHU_WEBHOOK_URL。")
            return

        # 构建卡片内容
        elements = [
            {
                "tag": "div",
                "text": {
                    "content": content,
                    "tag": "lark_md"
                }
            }
        ]
        
        # 如果有图片则添加
        if image_key:
            elements.append({
                "tag": "img",
                "img_key": image_key,
                "alt": {
                    "content": "周价格趋势图",
                    "tag": "plain_text"
                }
            })

        card = {
            "header": {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                },
                "template": "blue"
            },
            "elements": elements
        }

        payload = {
            "msg_type": "interactive",
            "card": card
        }
        
        if self.webhook_secret:
            timestamp = str(int(time.time()))
            sign = self._gen_sign(timestamp, self.webhook_secret)
            payload["timestamp"] = timestamp
            payload["sign"] = sign

        try:
            resp = requests.post(self.webhook_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # 检查业务错误码
            code = data.get("code") if data.get("code") is not None else data.get("StatusCode")
            if code == 0:
                logger.info(f"交互式卡片已发送至飞书 - 标题: {title}")
            else:
                msg = data.get("msg") or data.get("StatusMessage") or "未知错误"
                logger.error(f"卡片消息下发失败 (业务错误) - 错误码: {code}, 原因: {msg}")
                # 记录 Payload 用于后续调试（去掉敏感信息）
                debug_payload = {k: v for k, v in payload.items() if k not in ["sign", "timestamp"]}
                logger.debug(f"失败的 Payload 内容: {json.dumps(debug_payload, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"发送卡片消息时发生网络异常: {e}")

if __name__ == "__main__":
    # 测试文本消息
    notifier = FeishuNotifier()
    notifier.send_text("CobaltGuard 通知组件已启动。")
