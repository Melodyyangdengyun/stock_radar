from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class StockKLine(BaseModel):
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    amount: float
    amplitude: Optional[float] = None
    change_pct: Optional[float] = None
    change_amount: Optional[float] = None
    turnover: Optional[float] = None


class StockInfo(BaseModel):
    symbol: str
    name: Optional[str] = None
    latest_price: Optional[float] = None
    change_pct: Optional[float] = None
    klines: List[StockKLine] = []


class LimitStock(BaseModel):
    code: str
    name: str
    change_pct: float
    latest_price: float
    amount: float
    float_market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    turnover: float
    industry: Optional[str] = None
    consecutive_days: Optional[int] = None


class SectorHeatMap(BaseModel):
    name: str
    change_pct: float
    volume: float
    amount: float
    stock_count: int
    up_count: int
    down_count: int


class FundFlow(BaseModel):
    code: str
    name: str
    main_inflow: float
    main_outflow: float
    retail_inflow: float
    retail_outflow: float
    net_inflow: float
    change_pct: float
