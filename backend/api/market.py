from fastapi import APIRouter, Query
from datetime import datetime
from services.stock_service import (
    get_limit_up_pool,
    get_limit_down_pool,
    get_sector_heatmap,
)
from services.cache_service import cache_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/limit-up")
async def get_limit_up(date: str = Query(None)):
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    cache_key = f"limit-up:{date}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    df = get_limit_up_pool(date)
    if df.empty:
        return {"date": date, "count": 0, "stocks": []}

    stocks = []
    for _, row in df.iterrows():
        stocks.append(
            {
                "code": str(row["代码"]),
                "name": str(row["名称"]),
                "change_pct": float(row["涨跌幅"]),
                "latest_price": float(row["最新价"]),
                "amount": float(row["成交额"]),
                "float_market_cap": float(row["流通市值"])
                if "流通市值" in row
                else None,
                "pe_ratio": float(row["动态市盈率"]) if "动态市盈率" in row else None,
                "turnover": float(row["换手率"]),
                "industry": str(row["所属行业"]) if "所属行业" in row else None,
                "consecutive_days": int(row["连板数"]) if "连板数" in row else None,
            }
        )

    result = {"date": date, "count": len(stocks), "stocks": stocks}
    cache_service.set(cache_key, result, ttl=120)
    return result


@router.get("/limit-down")
async def get_limit_down(date: str = Query(None)):
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    cache_key = f"limit-down:{date}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    df = get_limit_down_pool(date)
    if df.empty:
        return {"date": date, "count": 0, "stocks": []}

    stocks = []
    for _, row in df.iterrows():
        stocks.append(
            {
                "code": str(row["代码"]),
                "name": str(row["名称"]),
                "change_pct": float(row["涨跌幅"]),
                "latest_price": float(row["最新价"]),
                "amount": float(row["成交额"]),
                "float_market_cap": float(row["流通市值"])
                if "流通市值" in row
                else None,
                "pe_ratio": float(row["动态市盈率"]) if "动态市盈率" in row else None,
                "turnover": float(row["换手率"]),
                "industry": str(row["所属行业"]) if "所属行业" in row else None,
            }
        )

    result = {"date": date, "count": len(stocks), "stocks": stocks}
    cache_service.set(cache_key, result, ttl=120)
    return result


@router.get("/sector-heatmap")
async def get_heatmap():
    cache_key = "sector-heatmap"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    df = get_sector_heatmap()
    if df.empty:
        return {"sectors": []}

    sectors = []
    for _, row in df.iterrows():
        sectors.append(
            {
                "name": str(row["板块名称"]) if "板块名称" in row else str(row.iloc[1]),
                "change_pct": float(row["涨跌幅"]) if "涨跌幅" in row else 0,
                "amount": float(row["成交额"]) if "成交额" in row else 0,
                "stock_count": int(row["总家数"]) if "总家数" in row else 0,
                "up_count": int(row["上涨家数"]) if "上涨家数" in row else 0,
                "down_count": int(row["下跌家数"]) if "下跌家数" in row else 0,
            }
        )

    sectors.sort(key=lambda x: x["change_pct"], reverse=True)
    result = {"sectors": sectors}
    cache_service.set(cache_key, result, ttl=120)
    return result
