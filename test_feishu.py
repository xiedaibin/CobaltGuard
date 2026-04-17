import os
import logging
from dotenv import load_dotenv
from src.notifier import FeishuNotifier

# Setup minimal logging to see exactly what is happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_feishu():
    print("=== 开始测试飞书通知 ===")
    
    # 强制加载 .env 变量
    if load_dotenv():
        print("成功加载 .env 配置文件。")
    else:
        print("警告: 未能加载 .env 文件，如果后续缺少变量请检查路径。")
        
    url = os.getenv("FEISHU_WEBHOOK_URL")
    secret = os.getenv("FEISHU_WEBHOOK_SECRET")
    
    print(f"检测到的 Webhook URL: {url}")
    print(f"检测到的 Webhook Secret: {secret}")
    
    if not url:
        print("错误: 找不到 FEISHU_WEBHOOK_URL 环境变量！")
        return
        
    print("\n初始化 FeishuNotifier...")
    notifier = FeishuNotifier()
    
    print("\n尝试发送纯文本测试消息...")
    try:
        notifier.send_text("🚀 [单元测试] 飞书推送联调成功！收到此消息说明签名算法和 Webhook 配置均无误。")
        print("✅ 发送请求成功，请查看飞书客户端是否收到提醒！")
    except Exception as e:
        print(f"❌ 发送请求失败，详细报错: {e}")

if __name__ == "__main__":
    test_feishu()
