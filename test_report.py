from dotenv import load_dotenv
load_dotenv()
from src.service import CobaltService
import logging

logging.basicConfig(level=logging.INFO)
print("=== 开始手动生成并测试发送报告 ===")
service = CobaltService()
service.send_daily_report()
print("=== 测试发送结束 ===")
