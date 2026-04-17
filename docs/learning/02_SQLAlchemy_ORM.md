# SQLAlchemy ORM 真经：数据持久化艺术 🗄️

## 01: 什么是 ORM？
ORM (Object-Relational Mapping) 的意思是“对象关系映射”。它的核心作用是让你**不再手写复杂的 SQL 语句**。

### 核心对比
- **传统方式**：`INSERT INTO prices (date, price) VALUES ('2026-04-17', 345000);`
- **ORM 方式**：`db.add(CobaltPrice(price_date='2026-04-17', price=345000))`

---

## 02: 核心组件拆解 (`src/database.py`)

### 1. Engine (引擎)
```python
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
```
引擎是程序的“动力源”，它负责与 SQLite 文件建立物理连接。

### 2. SessionLocal (会话工厂)
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
Session 是你与数据库对话的“一次聊天窗口”。每次操作数据库，你都需要开一个 Session。

### 3. Base (基类)
```python
Base = declarative_base()
```
这是模型的母版。只有继承了它的类，才会被 SQLAlchemy 识别为数据库表。

### 4. 数据模型 (The Model)
```python
class CobaltPrice(Base):
    __tablename__ = "cobalt_prices"
    price_date = Column(String, primary_key=True, index=True)
    price = Column(Float)
    raw_text = Column(String)
```
在这里，你定义的每一个变量都对应数据库表中的一列。

---

## 03: 实践中的 CRUD (增删改查)
在 `src/service.py` 中，你可以看到这些模型的应用：

- **增加数据**：`db.add(new_price)`
- **提交保存**：`db.commit()`
- **过滤查询**：`db.query(CobaltPrice).filter(CobaltPrice.price_date == date).first()`

---

## 💡 为什么选择 SQLite？
本项目使用了 SQLite 数据库：
1. **零配置**：它只是一个名为 `cobalt.db` 的文件，不需要安装像 MySQL 这样的大型软件。
2. **原子性**：支持事务，保证在程序崩溃时数据不会损坏。
3. **便携性**：你可以直接把数据库文件复制走，在另一台电脑上直接用。
