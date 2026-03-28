from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import stocks, market
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stock Radar API",
    description="股票雷达 - A股数据分析API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(market.router)


@app.get("/")
async def root():
    return {"message": "Stock Radar API", "version": "2.0.0"}


@app.get("/health")
async def health():
    from services.cache_service import cache_service

    return {
        "status": "ok",
        "redis": "connected" if cache_service.is_connected() else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
