from dotenv import load_dotenv
load_dotenv()
from src.database import SessionLocal, CobaltPrice, init_db
from src.scraper import CobaltScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_historical_data():
    print("=== 开始抓取并初始化历史数据 ===")
    init_db()
    
    scraper = CobaltScraper()
    prices = scraper.fetch_all_prices()
    
    if not prices:
        print("未抓取到任何历史价格数据！请检查网络或网站结构。")
        return
        
    db = SessionLocal()
    try:
        added = 0
        updated = 0
        
        for entry in prices:
            existing = db.query(CobaltPrice).filter(CobaltPrice.price_date == entry['date']).first()
            if existing:
                existing.price = entry['price']
                existing.raw_text = entry['raw_text']
                updated += 1
            else:
                new_price = CobaltPrice(
                    price_date=entry['date'],
                    price=entry['price'],
                    raw_text=entry['raw_text']
                )
                db.add(new_price)
                added += 1
                
        db.commit()
        print(f"=== 历史数据初始化完成 ===")
        print(f"成功在页面找到: {len(prices)} 条记录")
        print(f"入库成功 -> 新增条目: {added} | 更新条目: {updated}")
    except Exception as e:
        print(f"保存数据库失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_historical_data()
