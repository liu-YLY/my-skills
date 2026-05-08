# Python 调试与问题定位参考

> **何时阅读**:仅在定位 Python 代码缺陷 / 审查 Python 代码 / 写 pytest 时查阅。**写测试用例、分析需求、提取测试点等非 Python 任务一律跳过**。
> **覆盖范围**:数据类型陷阱 + 异常处理 + 并发 + Flask 常见问题 + API 测试 + 排查工具 + pytest 要点。
> **可跳过条件**:本次任务不涉及 Python 代码（默认跳过）。
> **快速定位**:
> - 定位 Bug → 跳「问题定位工具箱」(日志/堆栈/网络/DB/内存)
> - 写 pytest → 跳末尾「pytest 测试框架要点」
> - 审 Flask 代码 → 跳「Web 框架常见问题」

## 代码审查检查清单

### 数据类型与转换

```python
# 危险：可变默认参数
def add_item(item, items=[]):  # 所有调用共享同一列表
    items.append(item)
    return items

# 安全写法
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

```python
# 危险：浅拷贝陷阱
config = {"db": {"host": "localhost", "port": 5432}}
backup = config.copy()  # 内层 dict 仍为同一引用
backup["db"]["port"] = 3306  # 同时修改了 config

# 安全写法
import copy
backup = copy.deepcopy(config)
```

### 异常处理

```python
# 危险：裸 except 吞没所有异常
try:
    result = process_data(data)
except:  # 包括 KeyboardInterrupt、SystemExit
    pass

# 安全写法：捕获具体异常并记录
try:
    result = process_data(data)
except (ValueError, KeyError) as e:
    logger.error(f"Data processing failed: {e}", exc_info=True)
    raise
```

```python
# 危险：资源泄漏
f = open("data.txt")
data = f.read()
# 如果前面抛异常，文件句柄不会释放

# 安全写法
with open("data.txt") as f:
    data = f.read()
```

### 并发与线程安全

```python
# 危险：无锁共享状态
counter = 0
def increment():
    global counter
    counter += 1  # 非原子操作

# 安全写法
import threading
lock = threading.Lock()
counter = 0
def increment():
    global counter
    with lock:
        counter += 1
```

```python
# 注意：asyncio 中的常见错误
async def fetch_all(urls):
    # 串行执行，未利用并发
    results = []
    for url in urls:
        result = await fetch(url)
        results.append(result)

    # 并发执行
    results = await asyncio.gather(*[fetch(url) for url in urls])
```

### 比较与身份

```python
# 陷阱：is vs ==
a = 256
b = 256
a is b  # True（小整数缓存）

a = 257
b = 257
a is b  # False（超出缓存范围）

# 规则：值比较用 ==，身份比较用 is
# 仅 None 检查用 is：if x is None
```

## Web 框架常见问题

### Flask

```python
# 问题：请求上下文外访问 request
from flask import request

def get_user_id():
    return request.args.get("user_id")  # 在请求上下文外调用会崩溃

# 解决：确保在视图函数或请求钩子中调用，或使用 test_request_context
```

```python
# 问题：JSON 序列化 date/datetime 失败
from datetime import date
from flask import jsonify

@app.route("/api/data")
def get_data():
    return jsonify({"date": date.today()})  # TypeError

# 解决：自定义序列化
def normalize_for_json(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
```

```python
# 问题：CORS 配置不生效
# 检查点：
# 1. flask-cors 是否正确初始化
# 2. 是否在蓝图级别也需要配置
# 3. 预检请求(OPTIONS)是否被拦截
```

### API 测试常见问题

```python
# 问题：PUT 请求未正确传递 Content-Type
import requests

# 错误
resp = requests.put(url, data=payload)  # 发送 form-encoded

# 正确
resp = requests.put(url, json=payload)  # 发送 application/json
```

```python
# 问题：响应状态码不一致
# 检查清单：
# - 200 OK → 成功获取资源
# - 201 Created → 成功创建资源
# - 204 No Content → 成功删除
# - 400 Bad Request → 请求参数错误
# - 401 Unauthorized → 未认证
# - 403 Forbidden → 无权限
# - 404 Not Found → 资源不存在
# - 409 Conflict → 资源冲突（重复）
# - 422 Unprocessable Entity → 业务校验失败
# - 429 Too Many Requests → 限流
# - 500 Internal Server Error → 服务端异常
```

## 问题定位工具箱

### 日志分析

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger(__name__)

# 关键位置打日志
logger.info("Processing request: %s", request.path)
logger.debug("Input data: %s", data)
logger.error("Failed to save: %s", e, exc_info=True)  # 包含堆栈
```

### 堆栈追踪分析

```python
import traceback

try:
    risky_operation()
except Exception:
    # 获取完整堆栈字符串
    tb = traceback.format_exc()
    logger.error("Operation failed:\n%s", tb)
```

**阅读堆栈的要点：**
1. 从底部开始读（最直接的异常原因）
2. 向上追溯调用链找到业务代码入口
3. 关注 `File "your_code.py"` 而非标准库/第三方库的帧
4. 注意 `Caused by` 或 `During handling of...` 的链式异常

### 网络问题排查

```bash
# 检查端口连通性
curl -v http://localhost:5000/api/health

# 查看请求/响应头
curl -i http://localhost:5000/api/files

# 带 JSON body 的 POST 请求
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 数据库问题排查

```python
# ORM N+1 查询检测
# 症状：页面加载慢，日志中大量 SELECT 语句
# 解决：使用 joinedload / subqueryload 预加载关联数据

# SQLAlchemy 示例
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.orders)).all()
```

### 内存与性能

```python
# 内存泄漏排查
import tracemalloc
tracemalloc.start()

# ... 执行操作 ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)
```

```python
# 性能分析
import cProfile
cProfile.run("target_function()", sort="cumulative")

# 或使用装饰器
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper
```

## pytest 测试框架要点

```python
# 参数化测试 - 数据驱动
import pytest

@pytest.mark.parametrize("input_val,expected", [
    ("https://example.com", True),
    ("http://example.com", True),
    ("ftp://example.com", False),
    ("example.com", False),
    ("", False),
    (None, False),
])
def test_validate_url(input_val, expected):
    assert validate_url(input_val) == expected
```

```python
# Fixture 管理测试数据
@pytest.fixture
def test_client(app):
    return app.test_client()

@pytest.fixture
def sample_test_case():
    return {
        "id": "TC_TEST_001",
        "title": "Sample test case",
        "priority": "P0",
        "type": "functional",
        "steps": ["Step 1", "Step 2"],
        "expected_results": ["Result 1"],
    }

def test_create_case(test_client, sample_test_case):
    resp = test_client.post("/api/cases", json=sample_test_case)
    assert resp.status_code == 201
```

```python
# Mock 外部依赖
from unittest.mock import patch, MagicMock

@patch("app.services.external_api.call")
def test_with_mock(mock_call):
    mock_call.return_value = {"status": "ok"}
    result = process_with_external()
    assert result["status"] == "ok"
    mock_call.assert_called_once()
```
