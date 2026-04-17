# CobaltGuard 技术进阶学习计划 🚀

本计划旨在通过 `CobaltGuard` 项目实践，帮助你从零掌握 **FastAPI**, **SQLAlchemy**, **APScheduler** 和 **Matplotlib** 等核心技术。

---

## 阶段一：FastAPI - 现代化的 Web 框架
> **目标**：理解为什么不再写 `Flask`。重点在于性能、自动文档和类型校验。

- [ ] **1.1 自动文档初探**
    - [ ] 理论：了解 OpenAPI (Swagger) 标准。
    - [ ] 实践：运行项目后访问 `/docs`，观察所有接口是如何自动生成的。
- [ ] **1.2 Pydantic 类型校验**
    - [ ] 理论：学习 Pydantic 模型如何定义数据结构。
    - [ ] 实践：阅读 `src/service.py` 中的 Schema 定义，理解 `CobaltPriceResponse`。
- [ ] **1.3 异步支持 (Async/Await)**
    - [ ] 理论：理解异步 IO 对高性能 Web 服务的重要性。
    - [ ] 实践：观察 `src/main.py` 中的 `async def` 定义。

---

## 阶段二：SQLAlchemy - 数据库 ORM 真经
> **目标**：像操作对象一样操作数据库，不再手写 SQL。

- [ ] **2.1 模型与映射 (Models)**
    - [ ] 理论：理解 Table 和 Python Class 的映射关系。
    - [ ] 实践：分析 `src/database.py` 中的 `CobaltPrice` 类定义。
- [ ] **2.2 Session 会话管理**
    - [ ] 理论：理解数据库连接池与 Session 的生命周期。
    - [ ] 实践：分析 `get_db` 依赖注入的写法。
- [ ] **2.3 复杂查询逻辑**
    - [ ] 理论：学习 Filter, Order_by 和 Limit。
    - [ ] 实践：在 `src/service.py` 中查看 `get_price_history` 的实现。

---

## 阶段三：APScheduler - 系统的“心跳”
> **目标**：让程序在无人值守时依然能按时工作。

- [ ] **3.1 任务调度类型 (Triggers)**
    - [ ] 理论：理解 `interval` (间隔) 与 `cron` (定时) 的区别。
    - [ ] 实践：查看 `src/main.py` 中 Scheduler 的配置方式。
- [ ] **3.2 后台运行机制**
    - [ ] 理论：了解 `BackgroundScheduler` 是如何不阻塞 Web 主线程的。
    - [ ] 实践：运行项目，观察日志是否在特定时间触发了爬虫。

---

## 阶段四：Matplotlib - 让数据“说话”
> **目标**：生成专业的商业报表图片。

- [ ] **4.1 Figure 与 Axes 的关系**
    - [ ] 理论：理解画布 (Figure) 和子图 (Axes) 的层级结构。
    - [ ] 实践：阅读 `src/reporter.py` 中的绘图函数。
- [ ] **4.2 解决中文字体问题**
    - [ ] 理论：了解 Python 在 Linux/Docker 环境下显示中文的痛点。
    - [ ] 实践：观察 `src/fonts/` 目录以及代码是如何加载 `.ttc` 字体的。
- [ ] **4.3 内存泄漏防范**
    - [ ] 理论：为什么绘图后必须调用 `plt.close()`。

---

## 阶段五：系统整合与工程化
> **目标**：掌握如何将零散的库拼装成一个健壮的生产系统。

- [ ] **5.1 依赖注入 (Dependency Injection)**
    - [ ] 理论：FastAPI 的 `Depends` 强大在哪里？
    - [ ] 实践：理解数据流如何从 API 传递到 Service 层。
- [ ] **5.2 重试机制与鲁棒性**
    - [ ] 实践：观察 `src/scraper.py` 中的异常处理逻辑。
- [ ] **5.3 Docker 容器化部署**
    - [ ] 理论：镜像分层与多阶段构建。
    - [ ] 实践：阅读 `Dockerfile`，理解如何安装中文字体依赖。

---

## 💡 学习建议
1. **对比法**：尝试把一个 `Get` 接口改成 `Post`，看看 Swagger 会发生什么变化。
2. **破坏法**：删掉数据库文件，观察 SQLAlchemy 是否能自动重建表。
3. **日志法**：在每个关键步骤加入 `logger.info()`，通过日志观察各模块的协作顺序。

---
*保持好奇心，代码是最好的教科书。*
