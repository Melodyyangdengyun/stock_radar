"""
Stock Radar - 股票雷达
扫描市场，捕捉机会，发现潜力股

功能概述：
1. 批量查询指定股票的历史K线数据
2. 获取跌停板股票池
3. 获取涨停板股票池
4. 定时任务（交易日自动执行）
5. 输出格式：Markdown

依赖库：
- akshare: 数据获取（免费，无需API Key）
- pandas: 数据处理
- apscheduler: 定时任务调度
- logging: 日志记录

使用方法：
    # 批量查询指定股票
    python stock_radar.py query 000001 600519 300750

    # 查询跌停板
    python stock_radar.py limit-down

    # 查询涨停板
    python stock_radar.py limit-up

    # 启动定时任务
    python stock_radar.py schedule
"""

import os
import argparse
from datetime import datetime, timedelta
import pandas as pd
import akshare as ak
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

# ==================== 配置区 ====================
DATA_DIR = "./radar_data"
LOG_FILE = f"{DATA_DIR}/radar.log"

# 创建数据目录
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ==================== Markdown格式化 ====================
def format_to_markdown(df: pd.DataFrame, title: str = "") -> str:
    """
    将DataFrame转换为Markdown表格

    Args:
        df: 数据DataFrame
        title: 标题

    Returns:
        str: Markdown格式字符串
    """
    if df.empty:
        return f"## {title}\n\n无数据\n"

    md = f"## {title}\n\n"

    # 表头
    columns = df.columns.tolist()
    md += "| " + " | ".join(str(c) for c in columns) + " |\n"
    md += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    # 数据行
    for _, row in df.iterrows():
        values = []
        for v in row:
            if pd.isna(v):
                values.append("-")
            elif isinstance(v, float):
                values.append(f"{v:.2f}")
            else:
                values.append(str(v))
        md += "| " + " | ".join(values) + " |\n"

    return md


def format_stock_summary(df: pd.DataFrame, symbol: str) -> str:
    """
    格式化单只股票的摘要信息

    Args:
        df: 股票K线数据
        symbol: 股票代码

    Returns:
        str: Markdown格式的摘要
    """
    if df.empty:
        return f"### {symbol}\n\n无数据\n"

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    # 计算涨跌幅
    change_pct = (
        ((latest["收盘"] - prev["收盘"]) / prev["收盘"]) * 100
        if prev["收盘"] != 0
        else 0
    )

    md = f"### {symbol}\n\n"
    md += f"- **最新价**: {latest['收盘']:.2f}\n"
    md += f"- **涨跌幅**: {change_pct:+.2f}%\n"
    md += f"- **最高**: {latest['最高']:.2f}\n"
    md += f"- **最低**: {latest['最低']:.2f}\n"
    md += f"- **成交量**: {latest['成交量']:,.0f}\n"
    md += f"- **成交额**: {latest['成交额']:,.0f}\n"
    md += f"- **日期**: {latest['日期']}\n"

    return md


# ==================== 核心功能模块 ====================
def query_single_stock(
    symbol: str, period: str = "daily", days: int = 30
) -> pd.DataFrame:
    """
    查询单只股票的历史K线数据

    Args:
        symbol: 股票代码，如 "000001"
        period: K线周期 (daily/weekly/monthly)
        days: 查询天数

    Returns:
        pd.DataFrame: K线数据
    """
    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )
        return df
    except Exception as e:
        logger.error(f"查询股票 {symbol} 失败: {e}")
        return pd.DataFrame()


def batch_query_stocks(symbols: list, period: str = "daily", days: int = 30) -> str:
    """
    批量查询多只股票，返回Markdown格式

    Args:
        symbols: 股票代码列表，如 ["000001", "600519", "300750"]
        period: K线周期 (daily/weekly/monthly)
        days: 查询天数

    Returns:
        str: Markdown格式的结果
    """
    if not symbols:
        return "## 批量查询结果\n\n请提供股票代码\n"

    logger.info(f"开始批量查询 {len(symbols)} 只股票...")

    md = f"# 批量查询结果\n\n"
    md += f"**查询时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**查询周期**: {period}\n"
    md += f"**查询天数**: {days}\n"
    md += f"**股票数量**: {len(symbols)}\n\n"
    md += "---\n\n"

    results = []
    for symbol in symbols:
        logger.info(f"正在查询 {symbol}...")
        df = query_single_stock(symbol, period, days)

        if not df.empty:
            # 只保留最近5条数据用于展示
            df_display = df.tail(5).copy()
            df_display["股票代码"] = symbol

            # 重命名列
            column_mapping = {
                "日期": "日期",
                "开盘": "开盘",
                "收盘": "收盘",
                "最高": "最高",
                "最低": "最低",
                "成交量": "成交量",
                "成交额": "成交额",
                "振幅": "振幅%",
                "涨跌幅": "涨跌幅%",
                "涨跌额": "涨跌额",
                "换手率": "换手率%",
            }
            df_display = df_display.rename(columns=column_mapping)

            results.append(
                {
                    "symbol": symbol,
                    "summary": format_stock_summary(df, symbol),
                    "data": df_display,
                }
            )
            logger.info(f"{symbol}: 查询成功，共 {len(df)} 条数据")
        else:
            results.append(
                {
                    "symbol": symbol,
                    "summary": f"### {symbol}\n\n查询失败或无数据\n",
                    "data": pd.DataFrame(),
                }
            )
            logger.warning(f"{symbol}: 查询失败或无数据")

    # 生成汇总信息
    md += "# 汇总信息\n\n"
    for r in results:
        md += r["summary"] + "\n"

    md += "---\n\n"

    # 生成详细数据表格
    md += "# 详细数据（最近5个交易日）\n\n"
    for r in results:
        if not r["data"].empty:
            md += format_to_markdown(r["data"], r["symbol"])
            md += "\n"

    logger.info(f"批量查询完成，共 {len(results)} 只股票")
    return md


def get_limit_down_pool(date: str = None) -> str:
    """
    获取跌停板股票池，返回Markdown格式

    Args:
        date: 日期，格式YYYYMMDD，默认今日

    Returns:
        str: Markdown格式的结果
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    logger.info(f"正在获取 {date} 跌停板数据...")

    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)

        md = f"# 跌停板池\n\n"
        md += f"**日期**: {date}\n"
        md += f"**跌停数量**: {len(df)} 只\n\n"
        md += "---\n\n"

        if not df.empty:
            # 选择关键列
            columns_to_show = [
                "代码",
                "名称",
                "涨跌幅",
                "最新价",
                "成交额",
                "流通市值",
                "动态市盈率",
                "换手率",
                "所属行业",
            ]
            available_cols = [col for col in columns_to_show if col in df.columns]
            df_display = df[available_cols].copy()

            # 格式化数值
            if "涨跌幅" in df_display.columns:
                df_display["涨跌幅"] = df_display["涨跌幅"].apply(lambda x: f"{x:.2f}%")
            if "成交额" in df_display.columns:
                df_display["成交额"] = df_display["成交额"].apply(
                    lambda x: f"{x / 100000000:.2f}亿"
                )
            if "流通市值" in df_display.columns:
                df_display["流通市值"] = df_display["流通市值"].apply(
                    lambda x: f"{x / 100000000:.2f}亿"
                )
            if "换手率" in df_display.columns:
                df_display["换手率"] = df_display["换手率"].apply(lambda x: f"{x:.2f}%")

            md += format_to_markdown(df_display, "跌停股票列表")
        else:
            md += "今日无跌停股票\n"

        logger.info(f"跌停板查询完成，共 {len(df)} 只")
        return md

    except Exception as e:
        logger.error(f"获取跌停板数据失败: {e}")
        return f"# 跌停板池\n\n**错误**: {str(e)}\n"


def get_limit_up_pool(date: str = None) -> str:
    """
    获取涨停板股票池，返回Markdown格式

    Args:
        date: 日期，格式YYYYMMDD，默认今日

    Returns:
        str: Markdown格式的结果
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    logger.info(f"正在获取 {date} 涨停板数据...")

    try:
        df = ak.stock_zt_pool_em(date=date)

        md = f"# 涨停板池\n\n"
        md += f"**日期**: {date}\n"
        md += f"**涨停数量**: {len(df)} 只\n\n"
        md += "---\n\n"

        if not df.empty:
            # 选择关键列
            columns_to_show = [
                "代码",
                "名称",
                "涨跌幅",
                "最新价",
                "成交额",
                "流通市值",
                "动态市盈率",
                "换手率",
                "连板数",
                "所属行业",
            ]
            available_cols = [col for col in columns_to_show if col in df.columns]
            df_display = df[available_cols].copy()

            # 格式化数值
            if "涨跌幅" in df_display.columns:
                df_display["涨跌幅"] = df_display["涨跌幅"].apply(lambda x: f"{x:.2f}%")
            if "成交额" in df_display.columns:
                df_display["成交额"] = df_display["成交额"].apply(
                    lambda x: f"{x / 100000000:.2f}亿"
                )
            if "流通市值" in df_display.columns:
                df_display["流通市值"] = df_display["流通市值"].apply(
                    lambda x: f"{x / 100000000:.2f}亿"
                )
            if "换手率" in df_display.columns:
                df_display["换手率"] = df_display["换手率"].apply(lambda x: f"{x:.2f}%")

            md += format_to_markdown(df_display, "涨停股票列表")
        else:
            md += "今日无涨停股票\n"

        logger.info(f"涨停板查询完成，共 {len(df)} 只")
        return md

    except Exception as e:
        logger.error(f"获取涨停板数据失败: {e}")
        return f"# 涨停板池\n\n**错误**: {str(e)}\n"


# ==================== 交易日判断 ====================
def is_a_share_trading_day(date_input):
    """
    判断指定日期是否为A股交易日
    """
    try:
        date_obj = pd.to_datetime(date_input).normalize()
        df = ak.tool_trade_date_hist_sina()
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        return not df[df["trade_date"] == date_obj].empty
    except Exception as e:
        logger.error(f"获取交易日历时出错: {e}")
        weekday = date_obj.weekday()
        return weekday < 5


# ==================== 定时任务 ====================
def scheduled_task():
    """定时任务：获取跌停板和涨停板数据"""
    current_date = datetime.now().strftime("%Y-%m-%d")

    if not is_a_share_trading_day(current_date):
        logger.info(f"【{current_date}】非交易日，跳过任务")
        return

    logger.info(f"【{current_date}】交易日，开始执行定时任务")

    date_str = datetime.now().strftime("%Y%m%d")

    # 获取跌停板
    limit_down_md = get_limit_down_pool(date_str)
    save_markdown(limit_down_md, f"limit_down_{date_str}.md")

    # 获取涨停板
    limit_up_md = get_limit_up_pool(date_str)
    save_markdown(limit_up_md, f"limit_up_{date_str}.md")

    logger.info(f"定时任务完成")


def save_markdown(content: str, filename: str):
    """保存Markdown文件"""
    filepath = f"{DATA_DIR}/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"已保存至 {filepath}")


def start_scheduler():
    """启动定时任务调度器"""
    logger.info("启动 Stock Radar 定时任务调度器...")

    executors = {"default": ThreadPoolExecutor(4)}
    scheduler = BlockingScheduler(executors=executors, timezone="Asia/Shanghai")

    # 每日15:30执行（收盘后）
    scheduler.add_job(
        func=scheduled_task,
        trigger="cron",
        hour=15,
        minute=30,
        id="daily_stock_task",
        replace_existing=True,
    )
    logger.info("已添加定时任务: 每个交易日 15:30 执行")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("接收到退出信号，正在关闭调度器...")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"调度器运行出错: {e}", exc_info=True)


# ==================== 命令行接口 ====================
def main():
    parser = argparse.ArgumentParser(
        description="Stock Radar - 股票雷达 | 扫描市场，捕捉机会",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s query 000001 600519 300750    # 批量查询指定股票
  %(prog)s query 000001 --period weekly  # 查询周K线
  %(prog)s query 000001 --days 60        # 查询60天数据
  %(prog)s limit-down                    # 查询跌停板
  %(prog)s limit-up                      # 查询涨停板
  %(prog)s schedule                      # 启动定时任务
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # query 子命令
    query_parser = subparsers.add_parser("query", help="批量查询指定股票")
    query_parser.add_argument("symbols", nargs="+", help="股票代码列表")
    query_parser.add_argument(
        "--period",
        default="daily",
        choices=["daily", "weekly", "monthly"],
        help="K线周期 (default: daily)",
    )
    query_parser.add_argument(
        "--days", type=int, default=30, help="查询天数 (default: 30)"
    )
    query_parser.add_argument("--output", "-o", help="输出文件路径")

    # limit-down 子命令
    limit_down_parser = subparsers.add_parser("limit-down", help="查询跌停板")
    limit_down_parser.add_argument("--date", help="日期，格式YYYYMMDD (default: 今日)")
    limit_down_parser.add_argument("--output", "-o", help="输出文件路径")

    # limit-up 子命令
    limit_up_parser = subparsers.add_parser("limit-up", help="查询涨停板")
    limit_up_parser.add_argument("--date", help="日期，格式YYYYMMDD (default: 今日)")
    limit_up_parser.add_argument("--output", "-o", help="输出文件路径")

    # schedule 子命令
    schedule_parser = subparsers.add_parser("schedule", help="启动定时任务")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "query":
        md = batch_query_stocks(args.symbols, args.period, args.days)

        if args.output:
            save_markdown(md, args.output)
        else:
            print(md)

    elif args.command == "limit-down":
        md = get_limit_down_pool(args.date)

        if args.output:
            save_markdown(md, args.output)
        else:
            print(md)

    elif args.command == "limit-up":
        md = get_limit_up_pool(args.date)

        if args.output:
            save_markdown(md, args.output)
        else:
            print(md)

    elif args.command == "schedule":
        start_scheduler()


# ==================== 入口点 ====================
if __name__ == "__main__":
    main()
