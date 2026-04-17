# FastAPI 核心基础知识 ⚡

## 01: FastAPI 自动文档初探 (Swagger UI)
在 FastAPI 中，文档是**实时自动生成**的。

### 核心概念：OpenAPI 与 Swagger
- **OpenAPI**: 一种描述 RESTful API 的行业标准。
- **Swagger UI**: 一个交互式工具，让你可以直接在网页上测试 API。

### 实践要点
- 启动服务后，默认访问路径为 `/docs`。
- 函数的 `Docstring` (文档字符串) 会被提取为接口描述。
- 函数参数的类型声明 (Type Hints) 会决定文档中的字段类型。

---

## 02: Pydantic 类型校验
Pydantic 是 Python 中数据验证的王者，FastAPI 与之完美集成。

### 核心价值
1. **数据清洗**：传入的字符串 "123" 会自动转为整数 123。
2. **安全性**：通过 `response_model` 过滤掉数据库中不应公开的敏感字段。
3. **合同规范**：前后端通过同一个 `Schema` 类进行沟通。

---

### 深入理解：什么是 `BaseModel`？
在你继承 `BaseModel` 的那一刻，你的普通 Python 类就变成了**“智能数据容器”**：
- **自动校验**：违反类型声明的数据会被拦截。
- **自动转换**：例如将字符串格式的日期自动转换为真正的日期对象。
- **一键 JSON 化**：`model.json()` 方法让数据传输变得极其简单。
- **配置灵活**：通过 `class Config` (在 Pydantic v2 中为 `model_config`) 可以开启 `from_attributes=True`，让模型能直接“吞下” SQLAlchemy 的数据库对象。

### 代码示例详解 (`src/schemas.py`)
```python
from pydantic import BaseModel
from typing import Optional

class CobaltPriceResponse(BaseModel):
    # 1. 继承 (BaseModel)：获得数据验证和序列化的超能力
    price_date: str
    price: float
    # 2. Optional[str] = None：声明为可选字段，且默认值为 None，增强容错性
    raw_text: Optional[str] = None

    class Config:
        # 3. 嵌套配置类：开启 from_attributes 允许直接读取 SQLAlchemy 等 ORM 对象属性
        from_attributes = True
```

---

## 03: 异步支持 (Async/Await)
FastAPI 的高性能很大程度上归功于其对异步编程的原生支持。

### 理论：阻塞 vs 非阻塞
- **阻塞 (Blocking)**：代码按照顺序一行行执行，网络请求没回来，后续代码就得等。
- **非阻塞 (Non-blocking)**：发起请求后，CPU 可以转头去处理其他任务，等请求回来再继续。

### 实践：什么时候用 `async`？
1. **网络请求**：调用外部 API 或抓取网页。
2. **磁盘 IO**：读取超大文件。
3. **数据库查询**：如果数据库驱动支持异步（如 `asyncpg`）。

**注意**：如果你在 `async def` 里调用了一个非常耗时的同步函数（即不带 `await` 的），它依然会卡死整个服务。

---

## 深度解析：生命周期与装饰器

### 1. 什么是 `lifespan`？
`lifespan` 函数就像程序的“出生证明”和“遗嘱”。它确保了资源（如数据库连接、定时任务）在程序启动时被正确初始化，在退出时被优雅关闭。

### 2. `@asynccontextmanager` 装饰器
这是 Python 实现“三段式”管理的标准方案：
- **第一段 (yield 前)**：启动逻辑。
- **第二段 (yield)**：挂起，等待主程序运行。
- **第三段 (yield 后)**：清理逻辑。

### 3. 如何阅读复杂的类型提示？
当你看到 `(A) -> B | C` 时：
- `->`：函数返回什么。
- `|`：类型 A 或者类型 B。
- `Mapping` / `Sequence`：Python 对字典和列表的专业称呼。
这种提示主要是给 IDE 看的，用于在你写错时给出波浪线警告。

---

## Python 幕后英雄：Dunder 魔法
在代码中你看到了 `__dict__` 这样的写法，这叫 **Dunder (Double Under)** 属性。

1. **约定俗成**：双下划线开头和结尾的变量是 Python 的内置特殊接口。
2. **`__dict__` 的本质**：它是对象的“映射字典”，存储了对象所有的实例属性。
3. **调试利器**：当你无法直接看清一个对象的内容时，打印它的 `__dict__` 是最快的方法。

---

## 进阶知识：为什么使用 `python -m`？
当你运行 `python -m src.main` 而不是 `python src/main.py` 时，你是在以“模块模式”运行程序。

### 核心区别
1. **识别包结构**：允许代码中使用 `.` 开头的相对导入（如 `from .service import ...`）。
2. **根目录对齐**：将执行命令的当前目录加入搜索路径，确保跨文件夹的 `import` 能够正常工作。
3. **官方推荐**：对于包含多个文件互相调用的复杂项目，使用 `-m` 是最健壮的启动方式。
