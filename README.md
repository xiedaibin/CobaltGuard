# CobaltGuard (钴价监测预警系统) 🛡️

CobaltGuard 是一个专门为金属钴市场设计的自动化价格监测与分析系统。它能够每日从生意社（100ppi.com）抓取最新钴价，通过内置的策略引擎计算波动率，并利用飞书（Lark）机器人实时推送预警信息和可视化趋势报表。

## 🌟 核心功能

*   **自动化采集**：每日 8:00 自动抓取生意社最新的金属钴市场价格。
*   **智能预警**：对比 30 天前的价格，当涨跌幅超过 **5%** 时，触发飞书实时告警。
*   **富媒体报表**：每日 9:00 自动生成最近 30 天的价格走势折线图，并推送到指定的飞书频道。
*   **RESTful API**：提供了完善的接口用于查询历史数据和手动触发任务。
*   **容器化部署**：支持 Docker One-Click 部署，内置中文字体支持。

## 🛠️ 技术架构

*   **Backend**: FastAPI, Python 3.10+
*   **Database**: SQLite (通过 SQLAlchemy ORM 管理)
*   **Task Management**: APScheduler (应用内常驻任务)
*   **Spider**: Requests + BeautifulSoup4 (轻量级高效抓取)
*   **Visualization**: Matplotlib (生成带中文字体的专业图表)
*   **Notifications**: Feishu (Lark) Webhook & App API

## 🚀 快速启动

### 1. 环境准备
确保您的机器上安装了 `Docker` 和 `Docker Compose`。

### 2. 配置文件
在工程根目录（开发）或 `deploy/` 目录（发布）下创建 `.env` 文件。模板参考：
```bash
FEISHU_WEBHOOK_URL=https://open.feishu.cn/...
FEISHU_APP_ID=cli_...
FEISHU_APP_SECRET=...
```

### 3. 运行项目
使用发布目录进行一键启动：
```bash
cd deploy
docker compose up -d
```

### 4. 数据初始化
首次启动后，容器内可能没有历史数据，请执行一次初始化脚本：
```bash
docker exec -it cobalt-guard python test_init.py
```

## 📡 接口说明 (API v1)

系统启动后，您可以访问 `http://localhost:8000/docs` 查看 Swagger 文档。

| 方法 | 路径 | 功能说明 |
| :-- | :-- | :-- |
| `GET` | `/api/v1/prices` | 查询最近的价格记录列表 |
| `GET` | `/api/v1/prices/{date}` | 获取指定日期的价格 (格式: YYYY-MM-DD) |
| `POST` | `/api/v1/trigger/collect` | **手动触发**一次实时数据采集与波动预警 |
| `POST` | `/api/v1/trigger/report` | **手动触发**一次每日报表（图表）的生成与发送 |

## 📁 目录结构

*   `src/`: 核心源代码 (Scraper, Reporter, Strategy 等)
*   `deploy/`: 生产环境部署配置
*   `data/`: SQLite 数据库存储目录 (持久化卷)
*   `logs/`: 系统运行日志目录
*   `test_init.py`: 历史数据同步/初始化工具

## 📜 维护说明

*   **数据持久化**：数据库存储在 `./data/cobalt.db`，请务必定期备份此目录。
*   **时区设置**：系统强制运行在 `Asia/Shanghai` 时区，以确保定时任务准时触发。
*   **日志**：可以通过 `docker logs -f cobalt-guard` 或查看 `./logs/` 目录获取详细运行信息。
