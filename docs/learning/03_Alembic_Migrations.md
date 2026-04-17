# Alembic：数据库的版本管理神器 🛰️

## 01: 为什么需要 Alembic？
在开发过程中，你的模型（Model）会不可避免地发生变化（增加字段、重命名等）。
- **Base.metadata.create_all**：只能创建，不能更新。
- **Alembic**：像 Git 一样，追踪数据库结构的变化，支持升级和回滚。

---

## 02: 核心命令（三板斧）

### 1. 生成记录 (Revision)
```bash
alembic revision --autogenerate -m "描述你的改动"
```
- **原理**：对比代码里的 `Base.metadata` 和数据库里的真实表结构，自动生成 Python 迁移脚本。

### 2. 执行升级 (Upgrade)
```bash
alembic upgrade head
```
- **注意**：`head` 代表最新的版本。

### 3. 执行降级 (Downgrade)
```bash
alembic downgrade -1
```
- **作用**：撤销上一次的数据库结构变更。

---

## 03: “后悔药”机制
这是刚才我们实战中最重要的部分：

### 场景 A：脚本生成了，但还没 upgrade
- **操作**：直接去 `alembic/versions/` 目录下删除对应的 `.py` 文件。
- **代价**：零代价，系统会当做没发生过。

### 场景 B：脚本已经执行 upgrade 到了数据库
- **操作**：
    1. 先执行 `alembic downgrade -1` 将数据库回滚。
    2. 再去 `alembic/versions/` 删除脚本。
- **代价**：会丢失该版本中新加字段里的数据（如果有的话）。

---

## 04: 配置避坑指南 (Windows 专用)

### 如何让 Alembic 认识 `src` 文件夹？
在 `alembic/env.py` 中，必须手动加入以下代码：
```python
import os
import sys
# 将项目根目录加入搜索路径
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
```

---

## 💡 职业建议
学会了 Alembic，你就拥有了“不删库也能改结构”的能力。在生产环境中，**严禁使用删除数据库文件的方式来更新结构**。
