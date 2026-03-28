from fastapi import APIRouter, Query
from typing import Optional
from services.stock_service import get_stock_kline, get_fund_flow
from services.cache_service import cache_service

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{symbol}")
async def get_stock_data(
    symbol: str,
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(90, ge=1, le=365),
):
    cache_key = f"stock:{symbol}:{period}:{days}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    df = get_stock_kline(symbol, period, days)
    if df.empty:
        return {"symbol": symbol, "error": "No data found"}

    klines = []
    for _, row in df.iterrows():
        klines.append(
            {
                "date": str(row["日期"]),
                "open": float(row["开盘"]),
                "close": float(row["收盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
                "amplitude": float(row["振幅"]) if "振幅" in row else None,
                "change_pct": float(row["涨跌幅"]) if "涨跌幅" in row else None,
                "change_amount": float(row["涨跌额"]) if "涨跌额" in row else None,
                "turnover": float(row["换手率"]) if "换手率" in row else None,
            }
        )

    result = {
        "symbol": symbol,
        "period": period,
        "days": days,
        "count": len(klines),
        "klines": klines,
    }

    cache_service.set(cache_key, result, ttl=120)
    return result


@router.get("/{symbol}/fund-flow")
async def get_stock_fund_flow(symbol: str):
    cache_key = f"fundflow:{symbol}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    df = get_fund_flow(symbol)
    if df.empty:
        return {"symbol": symbol, "error": "No data found"}

    result = {
        "symbol": symbol,
        "data": df.to_dict(orient="records"),
    }

    cache_service.set(cache_key, result, ttl=60)
    return result
