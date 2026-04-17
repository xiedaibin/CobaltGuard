# CobaltGuard 实施计划 (Plan.md)

## 1. 准备阶段 (Research & Environment)
- [x] 目标网页 HTML 结构分析 (2026-04-10)
- [ ] 创建项目目录结构 (src, data, tests)
- [ ] 编写 `requirements.txt`

## 2. 核心模块开发 (Core Modules)
- [ ] **Data Layer**: 实现 SQLAlchemy 模型 `CobaltPrice` 及 SQLite 初始化脚本。
- [ ] **Scraper Layer**: 编写采集脚本，支持从 `100ppi.com` 提取价格并入库。
- [ ] **Notifier Layer**: 封装飞书机器人 API（包括图片上传和消息推送）。
- [ ] **Strategy Layer**: 实现“月度波动率 > 5%”的计算逻辑。
- [ ] **Reporter Layer**: 使用 Matplotlib 生成最近 7 天价格折线图。

## 3. Web 接口与任务调度 (FastAPI & Scheduler)
- [ ] **API Layer**: 实现查询、周报生成和手动触发采集的 RESTful API。
- [ ] **Scheduler Layer**: 集成 APScheduler，设定 8:00 采集和 9:00 报告任务。

## 4. 容器化与部署 (Dockerization)
- [ ] 编写 `Dockerfile` (包含中文字体安装)。
- [ ] 编写 `docker-compose.yml`。
- [ ] 编写环境配置文件 `.env.example`。

## 5. 验证与交付 (Validation)
- [ ] 单元测试：验证爬虫正则匹配逻辑。
- [ ] 集成测试：模拟 30 天前数据，触发 5% 波动告警。
- [ ] 接口测试：通过 Swagger UI 验证 API 响应。

---

## 关键技术文档记录
1. **数据抓取验证 (Scraper Doc)**: 记录抓取的正则表达式及异常处理。
2. **飞书交互协议 (Feishu Doc)**: 记录如何通过 Webhook 推送带图片的消息。
3. **策略算法 (Strategy Doc)**: 详细说明波动率计算公式及历史数据取值逻辑。
