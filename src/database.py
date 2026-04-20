from sqlalchemy import Column, Integer, Float, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# 数据库连接 URL，优先从环境变量读取
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/cobalt.db")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CobaltPrice(Base):
    """钴价格数据模型"""
    __tablename__ = "cobalt_prices"

    id = Column(Integer, primary_key=True, index=True)
    price_date = Column(String, unique=True, index=True)  # 日期格式: YYYY-MM-DD
    price = Column(Float, nullable=False)                # 价格（元/吨）
    raw_text = Column(String)                           # 抓取到的原始文本内容
    created_at = Column(DateTime, server_default=func.now()) # 记录创建时间 
    #comment = Column(String, nullable=True)

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)

from contextlib import contextmanager

def get_db():
    """获取数据库会话的依赖项 (用于 FastAPI 依赖注入)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def session_scope():
    """上下文管理器，用于在非请求流程中安全管理 Session。
    用法: with session_scope() as db: ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
