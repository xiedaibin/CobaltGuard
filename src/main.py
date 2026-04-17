from fastapi import FastAPI, HTTPException, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .service import CobaltService
from . import schemas
from typing import List
import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()
import logging
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

service = CobaltService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动阶段：初始化调度器
    scheduler = BackgroundScheduler()
    
    # 早上 8:00 - 数据采集与波动预警检查
    scheduler.add_job(
        service.run_daily_collection,
        trigger=CronTrigger(hour=8, minute=0),
        id="collect_task",
        name="抓取与波动分析",
        replace_existing=True
    )
    
    # 早上 9:00 - 发送每日报表
    scheduler.add_job(
        service.send_daily_report,
        trigger=CronTrigger(hour=9, minute=0),
        id="report_task",
        name="生成并发送每日报表",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("调度器已启动。每日 8:00 采集数据，9:00 发送报表。")
    
    yield
    
    # 关闭阶段
    scheduler.shutdown()
    logger.info("调度器已关闭。")

app = FastAPI(title="CobaltGuard API (钴价格监测系统)", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "CobaltGuard API 正在运行。"}

@app.get("/api/v1/prices", response_model=List[schemas.CobaltPriceResponse])
def get_prices(limit: int = 10):
    """查询历史价格数据列表"""
    result = service.get_prices(limit)
    logger.info(f"查询历史价格数据列表，limit: {limit}, result: {[p.__dict__ for p in result]}")
    logger.info(f"查询历史价格数据列表2，limit: {limit}, result: {[schemas.CobaltPriceResponse.from_orm(p).dict() for p in result]}")
    return result

@app.get("/api/v1/prices/{date_str}", response_model=schemas.CobaltPriceResponse)
def get_price_by_date(date_str: str):
    """按日期查询具体价格"""
    price = service.get_price_by_date(date_str)
    if not price:
        raise HTTPException(status_code=404, detail="未找到该日期的价格数据。")
    return price

@app.post("/api/v1/trigger/collect")
def trigger_collect():
    """手动触发数据采集流程"""
    service.run_daily_collection()
    return {"status": "采集任务已触发。"}

@app.post("/api/v1/trigger/report")
def trigger_report():
    """手动触发每日报表发送流程"""
    service.send_daily_report()
    return {"status": "报表生成任务已触发。"}

if __name__ == "__main__":
    # 使用字符串路径并开启 reload=True
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
