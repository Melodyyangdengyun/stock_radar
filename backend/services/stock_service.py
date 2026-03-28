import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def get_stock_kline(symbol: str, period: str = "daily", days: int = 90) -> pd.DataFrame:
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )
        return df
    except Exception as e:
        logger.error(f"Query stock {symbol} failed: {e}")
        return pd.DataFrame()


def get_limit_up_pool(date: str = None) -> pd.DataFrame:
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_em(date=date)
        return df
    except Exception as e:
        logger.error(f"Query limit-up pool failed: {e}")
        return pd.DataFrame()


def get_limit_down_pool(date: str = None) -> pd.DataFrame:
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
        return df
    except Exception as e:
        logger.error(f"Query limit-down pool failed: {e}")
        return pd.DataFrame()


def get_sector_heatmap() -> pd.DataFrame:
    try:
        df = ak.stock_board_industry_name_em()
        return df
    except Exception as e:
        logger.error(f"Query sector heatmap failed: {e}")
        return pd.DataFrame()


def get_fund_flow(symbol: str = None) -> pd.DataFrame:
    try:
        if symbol:
            df = ak.stock_individual_fund_flow(stock=symbol, market="sh")
        else:
            df = ak.stock_market_fund_flow()
        return df
    except Exception as e:
        logger.error(f"Query fund flow failed: {e}")
        return pd.DataFrame()
