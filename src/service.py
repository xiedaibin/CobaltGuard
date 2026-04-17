import pandas as pd
from datetime import datetime
import logging
from .database import SessionLocal, CobaltPrice, init_db
from .scraper import CobaltScraper
from .notifier import FeishuNotifier
from .reporter import CobaltReporter
from .strategy import PriceStrategy

logger = logging.getLogger(__name__)

class CobaltService:
    def __init__(self):
        init_db()
        self.scraper = CobaltScraper()
        self.notifier = FeishuNotifier()
        self.reporter = CobaltReporter()

    def run_daily_collection(self):
        """
        核心任务：抓取 -> 保存 -> 策略检查 -> 预警
        """
        logger.info("开始每日价格采集...")
        result = self.scraper.fetch_latest_price()
        if not result:
            logger.error("抓取最新价格失败。")
            return

        db = SessionLocal()
        try:
            # 1. 检查该日期的价格是否已存在
            existing = db.query(CobaltPrice).filter(CobaltPrice.price_date == result['date']).first()
            if existing:
                logger.info(f"{result['date']} 的价格已存在，正在更新数据...")
                existing.price = result['price']
                existing.raw_text = result['raw_text']
            else:
                new_price = CobaltPrice(
                    price_date=result['date'],
                    price=result['price'],
                    raw_text=result['raw_text']
                )
                db.add(new_price)
            db.commit()

            # 2. 策略检查：对比 30 天前的波动率是否超过 5%
            # 获取历史数据
            all_prices = db.query(CobaltPrice).all()
            df = pd.DataFrame([{ "price_date": p.price_date, "price": p.price } for p in all_prices])
            
            triggered, fluctuation, ref_date = PriceStrategy.check_volatility(result['price'], result['date'], df)
            
            if triggered:
                alert_msg = f"⚠️ **价格波动预警**\n\n当前价格: **{result['price']}** ({result['date']})\n对比价格: **{df[df['price_date']==ref_date]['price'].iloc[0]}** ({ref_date})\n波动幅度: **{fluctuation:+.2%}**\n\n波动超过 5% 触发预警。"
                self.notifier.send_text(alert_msg)

        except Exception as e:
            logger.error(f"run_daily_collection 运行出错: {e}")
            db.rollback()
        finally:
            db.close()

    def send_daily_report(self):
        """
        核心任务：生成周趋势图 -> 格式化摘要 -> 发送到飞书
        """
        logger.info("正在生成并发送每日报表...")
        db = SessionLocal()
        try:
            all_prices = db.query(CobaltPrice).order_by(CobaltPrice.price_date.desc()).limit(30).all()
            if not all_prices:
                logger.warning("没有可用于生成报表的价格数据。")
                return

            df = pd.DataFrame([{ "price_date": p.price_date, "price": p.price } for p in all_prices])
            
            # 格式化文字摘要
            summary = self.reporter.format_weekly_summary(df)
            
            # 生成图表
            chart_path = self.reporter.generate_weekly_chart(df)
            
            # 上传并发送
            image_key = None
            if chart_path:
                image_key = self.notifier.upload_image(chart_path)
            
            self.notifier.send_interactive_card(
                title="钴价格每日动态及趋势报告",
                content=summary,
                image_key=image_key
            )
            
        except Exception as e:
            logger.error(f"send_daily_report 运行出错: {e}")
        finally:
            db.close()

    def get_prices(self, limit: int = 10):
        """获取价格列表"""
        db = SessionLocal()
        try:
            return db.query(CobaltPrice).order_by(CobaltPrice.price_date.desc()).limit(limit).all()
        finally:
            db.close()

    def get_price_by_date(self, date_str: str):
        """按日期获取价格"""
        db = SessionLocal()
        try:
            return db.query(CobaltPrice).filter(CobaltPrice.price_date == date_str).first()
        finally:
            db.close()
