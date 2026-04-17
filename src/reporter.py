import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

class CobaltReporter:
    def __init__(self, output_dir="data/charts"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 配置 matplotlib 以支持 Docker/Linux/Windows 下的中文字体
        # 加载本地字体文件以确保环境一致性
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "wqy-zenhei.ttc")
        if os.path.exists(font_path):
            matplotlib.font_manager.fontManager.addfont(font_path)
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
        else:
            logger.warning(f"在 {font_path} 未找到字体文件，将回退到系统字体。")
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'sans-serif']
        
        plt.rcParams['axes.unicode_minus'] = False

    def generate_weekly_chart(self, prices_df: pd.DataFrame) -> str:
        """
        生成最近 7 条记录的折线图。
        返回保存的图片路径。
        """
        if prices_df.empty:
            logger.warning("数据表为空，无法生成图表。")
            return ""

        # 确保日期已排序并取最后 7 条
        df = prices_df.sort_values('price_date').tail(7)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['price_date'], df['price'], marker='o', linestyle='-', color='b')
        plt.title('最近一周钴价格变动趋势', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('价格 (元/吨)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        # 标注具体数值
        for x, y in zip(df['price_date'], df['price']):
            plt.text(x, y, f'{y:.0f}', ha='center', va='bottom')

        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"weekly_report_{timestamp}.png")
        plt.savefig(file_path)
        plt.close()
        
        logger.info(f"周报图表已保存至 {file_path}")
        return file_path

    def format_weekly_summary(self, prices_df: pd.DataFrame) -> str:
        """
        格式化价格变动的文字摘要。
        """
        if prices_df.empty:
            return "暂无数据"

        df = prices_df.sort_values('price_date', ascending=False)
        latest = df.iloc[0]
        
        summary = f"**今日钴价报告 ({latest['price_date']})**\n\n"
        summary += f"最新价格: **{latest['price']:.2f} 元/吨**\n"
        
        if len(df) >= 2:
            prev = df.iloc[1]
            diff = latest['price'] - prev['price']
            percent = (diff / prev['price']) * 100
            trend = "📈 上涨" if diff > 0 else "📉 下跌" if diff < 0 else "➖ 持平"
            summary += f"较前一交易日: {trend} {abs(diff):.2f} ({percent:+.2f}%)\n"
        
        if len(df) >= 7:
            week_ago = df.iloc[min(6, len(df)-1)]
            diff_w = latest['price'] - week_ago['price']
            percent_w = (diff_w / week_ago['price']) * 100
            summary += f"最近一周波动: {percent_w:+.2f}%\n"
            
        return summary
