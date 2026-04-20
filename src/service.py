import pandas as pd
import logging
from sqlalchemy.orm import Session
from .database import CobaltPrice, init_db, session_scope
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

    def run_daily_collection(self, db: Session):
        """
        核心任务：抓取 -> 保存 -> 策略检查 -> 预警
        """
        logger.info("开始每日价格采集...")
        result = self.scraper.fetch_latest_price()
        if not result:
            logger.error("抓取最新价格失败。")
            return

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
        
        # 强制更新缓存，确保后续查询能看到最新数据
        db.flush()

        # 2. 策略检查：对比 30 天前的波动率是否超过 5%
        all_prices = db.query(CobaltPrice).all()
        df = pd.DataFrame([{ "price_date": p.price_date, "price": p.price } for p in all_prices])
        
        triggered, fluctuation, ref_date = PriceStrategy.check_volatility(result['price'], result['date'], df)
        
        if triggered:
            alert_msg = f"⚠️ **价格波动预警**\n\n当前价格: **{result['price']}** ({result['date']})\n对比价格: **{df[df['price_date']==ref_date]['price'].iloc[0]}** ({ref_date})\n波动幅度: **{fluctuation:+.2%}**\n\n波动超过 5% 触发预警。"
            self.notifier.send_text(alert_msg)

    def send_daily_report(self, db: Session):
        """
        核心任务：生成周趋势图 -> 格式化摘要 -> 发送到飞书
        """
        logger.info("正在生成并发送每日报表...")
        all_prices = db.query(CobaltPrice).order_by(CobaltPrice.price_date.desc()).limit(30).all()
        if not all_prices:
            logger.warning("没有可用于生成报表的价格数据。")
            return

        df = pd.DataFrame([{ "price_date": p.price_date, "price": p.price } for p in all_prices])
        
        summary = self.reporter.format_weekly_summary(df)
        chart_path = self.reporter.generate_weekly_chart(df)
        
        image_key = None
        if chart_path:
            image_key = self.notifier.upload_image(chart_path)
        
        self.notifier.send_interactive_card(
            title="钴价格每日动态及趋势报告",
            content=summary,
            image_key=image_key
        )

    def get_prices(self, db: Session, limit: int = 10):
        """获取价格列表"""
        return db.query(CobaltPrice).order_by(CobaltPrice.price_date.desc()).limit(limit).all()

    def get_price_by_date(self, db: Session, date_str: str):
        """按日期获取价格"""
        return db.query(CobaltPrice).filter(CobaltPrice.price_date == date_str).first()
