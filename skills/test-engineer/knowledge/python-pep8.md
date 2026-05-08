# Python PEP 8 编码规范

> **何时阅读**:仅在审查 Python 代码 / 写 Python 自动化脚本 / 定位 Python 缺陷时查阅。
> **覆盖范围**:缩进/行宽/import/命名/空格/字符串/比较/异常/函数设计/docstring + 末尾 PEP 8 检查清单。
> **可跳过条件**:本次任务不涉及 Python 代码审阅或编写;项目主语言为非 Python。
> **快速定位**:对 Python 代码 spot-check → 直跳末尾「PEP 8 检查清单」表。

编写和审查 Python 代码时遵循此规范。代码审查、自动化测试脚本编写、缺陷定位时均以此为标准。

## 缩进与行宽

- 使用 **4 个空格**缩进，禁止 Tab
- 每行最长 **79 字符**，docstring/注释最长 72 字符
- 续行对齐方式：

```python
# 与左括号对齐
result = some_function(arg_one, arg_two,
                       arg_three, arg_four)

# 悬挂缩进（多加一层区分）
def long_function_name(
        var_one, var_two,
        var_three, var_four):
    print(var_one)

# if 条件过长时添加注释区分
if (condition_one
        and condition_two):
    # Both conditions satisfied.
    do_something()
```

## 空行

- 顶层函数和类定义之间：**2 个空行**
- 类内方法之间：**1 个空行**
- 函数内逻辑段落之间：酌情 1 个空行

```python
class MyClass:

    def method_one(self):
        pass

    def method_two(self):
        pass


def top_level_function():
    pass
```

## Import 规范

- 每个 import 独占一行
- 分组顺序：标准库 → 第三方库 → 本地模块，组间空一行
- 禁止 `from module import *`

```python
import os
import sys

from flask import Flask, jsonify
from ruamel.yaml import YAML

from app.utils import validate_input
from app.models import TestCase
```

## 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块 | `snake_case` | `test_utils.py` |
| 包 | `lowercase` | `testengine` |
| 类 | `PascalCase` | `TestCaseValidator` |
| 函数/方法 | `snake_case` | `validate_test_case()` |
| 变量 | `snake_case` | `file_path` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 私有 | 单下划线前缀 | `_internal_method()` |
| 强私有 | 双下划线前缀 | `__name_mangled` |
| 魔术方法 | 双下划线包裹 | `__init__`, `__str__` |

**命名禁忌：**
- 避免单字符变量（循环计数 `i`/`j`/`k` 除外）
- 避免 `l`（小写 L）、`O`（大写 o）、`I`（大写 i）作为变量名
- 布尔变量用 `is_`/`has_`/`can_` 前缀：`is_valid`, `has_permission`

## 空格使用

```python
# 赋值、比较运算符两侧各一个空格
x = 1
if x == 1:

# 函数参数默认值的等号两侧无空格
def func(key, value=None):

# 逗号/冒号/分号后加空格，前不加
items = [1, 2, 3]
mapping = {"key": "value"}

# 括号内侧不加空格
func(arg)          # 对
func( arg )        # 错

# 切片冒号两侧不加空格（或对称加）
items[1:3]         # 对
items[1 : 3]       # 对
items[1: 3]        # 错

# 不要用空格对齐赋值
x = 1              # 对
y = 2
long_variable = 3

x             = 1  # 错
y             = 2
long_variable = 3
```

## 字符串

- 单引号和双引号等价，项目内统一即可
- 优先使用 **f-string**（Python 3.6+）：

```python
name = "world"
greeting = f"Hello, {name}!"

# 多行用三引号
query = """
    SELECT *
    FROM users
    WHERE status = 'active'
"""
```

## 比较与布尔

```python
# 与 None 比较用 is / is not
if value is None:       # 对
if value == None:       # 错

# 布尔判断不要和 True/False 比较
if is_valid:            # 对
if is_valid == True:    # 错
if is_valid is True:    # 错

# 空容器判断用隐式布尔
if items:               # 对（非空）
if not items:           # 对（空）
if len(items) > 0:      # 冗余
if items != []:         # 冗余

# 用 isinstance() 代替 type()
if isinstance(obj, str):    # 对
if type(obj) is str:        # 避免
```

## 异常处理

```python
# 捕获具体异常，不要裸 except
try:
    value = data[key]
except KeyError:
    value = default_value

# 错误
try:
    value = data[key]
except:
    value = default_value

# 异常链：raise from 保留原始异常
try:
    result = int(text)
except ValueError as e:
    raise ValidationError(f"Invalid number: {text}") from e
```

## 函数设计

```python
# 返回值一致（不要混合返回 None 和有效值，除非是显式 Optional）
def find_user(user_id: str) -> Optional[User]:
    user = db.get(user_id)
    if user is None:
        return None
    return user

# 类型注解（Python 3.5+）
def validate_url(url: str) -> bool:
    ...

def process_items(items: list[str]) -> dict[str, int]:
    ...

# 参数过多时用关键字参数强制
def create_webhook(
    url: str,
    version: str,
    *,
    description: str = "",
    status: str = "active",
) -> dict:
    ...
```

## Docstring 规范

```python
def validate_test_case(data: dict) -> dict:
    """Validate test case data against the JSON schema.

    Args:
        data: Test case dictionary containing id, title, steps, etc.

    Returns:
        Dictionary with 'valid' (bool) and 'errors' (list) keys.

    Raises:
        FileNotFoundError: If schema file is missing.
    """
```

- 单行 docstring：`"""Return the user's full name."""`
- 多行 docstring：首行摘要 + 空行 + 详细说明
- 使用 Google 风格（Args/Returns/Raises）

## 审查代码时的 PEP 8 检查清单

| 检查项 | 快速判断 |
|--------|----------|
| 缩进 | 全部 4 空格，无 Tab 混用 |
| 行宽 | 无超 79 字符的行 |
| import | 分组正确，无 `*` 导入 |
| 命名 | 类 PascalCase，函数/变量 snake_case，常量 UPPER |
| 空格 | 运算符两侧、逗号后，括号内无多余 |
| 比较 | None 用 `is`，布尔不比较 True/False，空容器用隐式 |
| 异常 | 无裸 except，有 `from` 链 |
| 类型注解 | 公共函数有参数和返回值注解 |
| Docstring | 公共函数/类有 docstring |
