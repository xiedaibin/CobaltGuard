from fastapi import FastAPI, HTTPException, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .service import CobaltService
from .database import get_db, session_scope
from . import schemas
from typing import List
from sqlalchemy.orm import Session
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
    
    # 定义任务包装器，以便在后台线程中使用 session_scope
    def job_collect():
        with session_scope() as db:
            service.run_daily_collection(db)

    def job_report():
        with session_scope() as db:
            service.send_daily_report(db)

    # 早上 8:00 - 数据采集与波动预警检查
    scheduler.add_job(
        job_collect,
        trigger=CronTrigger(hour=8, minute=0),
        id="collect_task",
        name="抓取与波动分析",
        replace_existing=True
    )
    
    # 早上 9:00 - 发送每日报表
    scheduler.add_job(
        job_report,
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
def get_prices(limit: int = 10, db: Session = Depends(get_db)):
    """查询历史价格数据列表"""
    result = service.get_prices(db, limit)
    return result

@app.get("/api/v1/prices/{date_str}", response_model=schemas.CobaltPriceResponse)
def get_price_by_date(date_str: str, db: Session = Depends(get_db)):
    """按日期查询具体价格"""
    price = service.get_price_by_date(db, date_str)
    if not price:
        raise HTTPException(status_code=404, detail="未找到该日期的价格数据。")
    return price

@app.post("/api/v1/trigger/collect")
def trigger_collect(db: Session = Depends(get_db)):
    """手动触发数据采集流程"""
    service.run_daily_collection(db)
    return {"status": "采集任务已触发。"}

@app.post("/api/v1/trigger/report")
def trigger_report(db: Session = Depends(get_db)):
    """手动触发每日报表发送流程"""
    service.send_daily_report(db)
    return {"status": "报表生成任务已触发。"}

if __name__ == "__main__":
    # 使用字符串路径并开启 reload=True
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
