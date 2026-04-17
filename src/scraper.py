import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CobaltScraper:
    URL = "https://www.100ppi.com/kx/detail-message-67-13-1.html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }

    def fetch_latest_price(self):
        """
        使用 Requests 从 100ppi.com 抓取最新的钴价格。
        """
        try:
            logger.info(f"正在抓取 {self.URL}...")
            response = requests.get(self.URL, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
            
            # 生意社有时会有简单的 521 挑战，但通常 Requests 带上 UA 即可直达
            if "正在进行安全检查" in response.text:
                logger.warning("检测到安全检查，Requests 直接获取失败。")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 生意社的数据通常在 li 标签中
            items = soup.find_all('li')
            if not items:
                items = soup.select('.list-main li')

            for li in items:
                text = li.get_text()
                # 匹配：[钴]4月16日钴为414800.00 ... 参考价为414800.00
                if "钴" in text and "参考价" in text:
                    span = li.find('span')
                    raw_date = span.text.strip() if span else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    try:
                        dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                        date_str = dt.strftime("%Y-%m-%d")
                    except:
                        date_str = raw_date.split()[0] if " " in raw_date else raw_date

                    match = re.search(r'参考价为([\d\.]+)', text)
                    if match:
                        price = float(match.group(1))
                        logger.info(f"成功抓取数据：日期={date_str}, 价格={price}")
                        return {
                            "date": date_str,
                            "price": price,
                            "raw_text": text.strip()
                        }
            
            logger.warning("在 HTML 内容中未找到相关钴价数据。")
            return None

        except Exception as e:
            logger.error(f"Requests 抓取出错：{str(e)}")
            return None

    def fetch_all_prices(self):
        """
        抓取当前页面的所有历史钴价格条目。
        """
        results = []
        try:
            logger.info(f"正在访问 {self.URL} 获取历史数据...")
            response = requests.get(self.URL, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
            
            if "正在进行安全检查" in response.text:
                logger.warning("无法获取历史数据：检测到安全检查。")
                return results

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('li')
            if not items:
                items = soup.select('.list-main li')

            for li in items:
                text = li.get_text()
                if "钴" in text and "参考价" in text:
                    span = li.find('span')
                    raw_date = span.text.strip() if span else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                        date_str = dt.strftime("%Y-%m-%d")
                    except:
                        date_str = raw_date.split()[0] if " " in raw_date else raw_date

                    match = re.search(r'参考价为([\d\.]+)', text)
                    if match:
                        price = float(match.group(1))
                        logger.info(f"提取到记录：日期={date_str}, 价格={price}")
                        results.append({
                            "date": date_str,
                            "price": price,
                            "raw_text": text.strip()
                        })
            logger.info(f"共解析到 {len(results)} 条历史价格记录。")
            return results
        except Exception as e:
            logger.error(f"获取所有价格记录时出错：{str(e)}")
            return results

if __name__ == "__main__":
    scraper = CobaltScraper()
    result = scraper.fetch_latest_price()
    print(result)
