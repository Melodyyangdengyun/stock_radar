# Stock Radar v2.0 - 股票雷达

扫描市场，捕捉机会，发现潜力股

## 功能特性

- K线图可视化（专业级 TradingView 风格）
- 涨停板 / 跌停板股票池
- 板块热力图
- 资金流向分析
- 股票搜索与详情查看
- Redis 数据缓存
- Docker 容器化部署

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Astro 5 + Svelte 5 + Tailwind 4 |
| 后端 | FastAPI + Python 3.11 |
| 图表 | TradingView Lightweight Charts + ECharts |
| 缓存 | Redis 7 |
| 部署 | Docker + Docker Compose |
| 包管理 | Bun |

## 快速开始

### Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/Melodyyangdengyun/stock_radar.git
cd stock_radar

# 启动服务
docker compose up -d

# 访问
# 前端: http://localhost:4321
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 前端
cd frontend
bun install
bun run dev
```

### CLI 工具（原功能）

```bash
python stock_radar.py query 000001 600519 300750
python stock_radar.py limit-down
python stock_radar.py limit-up
python stock_radar.py schedule
```

## 项目结构

```
stock_radar/
├── docker-compose.yml      # Docker 编排
├── .env                    # 环境变量
├── backend/                # 后端服务
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py             # FastAPI 入口
│   ├── api/                # API 路由
│   ├── services/           # 业务逻辑
│   └── models/             # 数据模型
├── frontend/               # 前端项目
│   ├── Dockerfile
│   ├── package.json
│   ├── astro.config.mjs
│   └── src/
│       ├── pages/          # 页面路由
│       ├── components/     # Svelte 组件
│       └── lib/            # 工具库
├── stock_radar.py          # CLI 工具
└── skills/                 # 技能模块
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/stocks/{symbol}` | GET | 获取个股K线数据 |
| `/api/stocks/{symbol}/fund-flow` | GET | 个股资金流向 |
| `/api/market/limit-up` | GET | 涨停板池 |
| `/api/market/limit-down` | GET | 跌停板池 |
| `/api/market/sector-heatmap` | GET | 板块热力图数据 |

## 依赖库

- akshare: 数据获取（免费，无需API Key）
- pandas: 数据处理
- fastapi: Web 框架
- redis: 缓存
- echarts: 图表可视化
- lightweight-charts: K线图

## 许可证

MIT License
