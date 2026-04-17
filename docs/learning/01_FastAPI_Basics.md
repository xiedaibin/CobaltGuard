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

### 代码示例 (`src/schemas.py`)
```python
from pydantic import BaseModel

class CobaltPriceResponse(BaseModel):
    price_date: str
    price: float

    class Config:
        from_attributes = True # 允许从 SQLAlchemy 模型读取数据
```
通过在路由中使用 `response_model=List[CobaltPriceResponse]`，我们确保了 API 输出的规范性。
