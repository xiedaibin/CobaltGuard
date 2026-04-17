from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PriceStrategy:
    @staticmethod
    def check_volatility(current_price: float, current_date: str, historical_df: pd.DataFrame, days: int = 30) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        检查价格相对于约“days”天前是否波动超过 5%。
        返回 (是否触发, 波动百分比, 参与对比的参考日期)。
        """
        if historical_df.empty:
            return False, None, None

        # 将日期字符串转换为 datetime 对象以便进行准确比较
        current_dt = datetime.strptime(current_date, "%Y-%m-%d")
        target_dt = current_dt - timedelta(days=days)
        target_date_str = target_dt.strftime("%Y-%m-%d")

        # 排序并查找最接近目标日期的记录（在 7 天窗口期内）
        # 100ppi 可能不会每天都有数据（例如周末、节假日）
        df = historical_df.copy()
        df['dt'] = pd.to_datetime(df['price_date'])
        
        # 筛选目标日期之前的记录
        mask = (df['dt'] <= target_dt) & (df['dt'] >= target_dt - timedelta(days=7))
        ref_records = df[mask].sort_values('dt', ascending=False)

        if ref_records.empty:
            # 如果 30 天前没有精确记录，则取最早可用或最接近的记录
            logger.info(f"在 {target_date_str} 附近未找到价格记录。检查最早可用记录。")
            ref_records = df.sort_values('dt', ascending=True)
            if ref_records.empty:
                return False, None, None
        
        ref_record = ref_records.iloc[0]
        ref_price = ref_record['price']
        ref_date = ref_record['price_date']

        fluctuation = (current_price - ref_price) / ref_price
        
        # 如果绝对波动率 >= 5% (0.05)，则触发预警
        if abs(fluctuation) >= 0.05:
            logger.info(f"触发波动预警：相对于 {ref_date}，波动幅度为 {fluctuation:+.2%}")
            return True, fluctuation, ref_date
        
        return False, fluctuation, ref_date
