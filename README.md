# Stock Radar - 股票雷达

扫描市场，捕捉机会，发现潜力股

## 功能特性

- 批量查询指定股票的历史K线数据
- 获取跌停板股票池
- 获取涨停板股票池
- 定时任务（交易日自动执行）
- 输出格式：Markdown

## 安装依赖

```bash
python -m pip install akshare pandas apscheduler tenacity
```

## 使用方法

```bash
# 批量查询指定股票
python stock_radar.py query 000001 600519 300750

# 查询跌停板
python stock_radar.py limit-down

# 查询涨停板
python stock_radar.py limit-up

# 保存到文件
python stock_radar.py query 000001 -o output.md

# 启动定时任务
python stock_radar.py schedule
```

## 项目结构

```
Stock-Radar/
├── stock_radar.py      # 主程序
├── radar_data/         # 输出目录
│   └── radar.log       # 日志文件
└── README.md           # 项目说明
```

## 依赖库

- akshare: 数据获取（免费，无需API Key）
- pandas: 数据处理
- apscheduler: 定时任务调度
- logging: 日志记录

## 许可证

MIT License
