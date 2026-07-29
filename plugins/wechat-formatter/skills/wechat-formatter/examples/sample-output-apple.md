<!--
排版风格：苹果风 (apple)
适用场景：产品设计、架构哲学、技术选型、强调极简优雅的内容
推荐配色：深空灰 #1d1d1f + Apple 蓝 #0071e3
视觉特征：极简留白 + 圆角灰底卡片 + 无编号无 Emoji + 短段落多呼吸感
排版时间：2026-05-22
原始文件：sample-input-testing-guide.md
图片占位：0 处
代码块：2 处
-->

# 编写高质量测试用例的方法

编写测试用例看似简单，背后却需要深入的需求分析和系统的测试点提取。

> 测试用例的价值不在于数量，而在于覆盖了哪些关键路径。

—


## 理解需求

拿到需求，第一步不是打开模板，而是回答三个问题。

核心价值是什么、有哪些用户角色、涉及哪些数据流转。这三个问题决定了一个功能需要被测到什么程度。

以用户注册为例。表面看只有一句话——填写手机号完成注册。深入分析后，至少需要考虑手机号唯一性、密码强度规则、是否需要短信验证、不同渠道的流程是否一致。

需求不明确的地方不要做假设。列问题清单逐条确认，比返工整批用例代价低得多。

—


## 七维度扫描法

系统化提取测试点的方法，是对每个功能按七个维度逐一扫描。

每个维度都对应一类容易被忽略的场景。

- 正向功能：验证核心路径能否走通
- 反向校验：覆盖空值、格式错误、边界值
- 权限角色：不同用户看到什么、能做什么
- 状态联动：选项变化是否触发关联变化
- 边界限制：上限、下限、重复提交
- UI 交互：按钮状态、文案准确性、跳转逻辑
- 异常容错：网络断开、服务端 5xx、依赖超时

> 多数人只关注前两个维度。权限、状态联动、异常容错贡献了超过 60% 的生产事故。

—


## 编写规范

测试用例的核心字段包括 id、title、priority、steps、expected_results。

id 推荐格式 `TC_{模块}_{功能}_{序号}`，title 用动宾结构不超过 40 字符。priority 划分为 P0 到 P3，对应核心路径到探索式测试。steps 用祈使句，每步一个操作。

最重要的是 expected_results 必须与 steps 一一对应，一步一验。

```
id: TC_USER_REGISTER_001
title: 正确填写注册信息并提交
priority: P0
type: functional
preconditions:
  - 手机号未注册
  - 验证码服务正常
steps:
  - 打开注册页面
  - 输入有效手机号
  - 输入符合规则的密码
  - 点击注册按钮
expected_results:
  - 页面展示注册表单
  - 手机号输入框显示已输入内容
  - 密码以掩码形式显示
  - 提示注册成功并跳转登录页
```

—


## 一条用例一个逻辑

新手最容易犯的错误，是把必填校验、格式校验、边界值校验全塞进一条用例。

用例失败后无法定位是哪个校验触发的。

正确做法是每个测试逻辑独立成一条用例。同一逻辑下不同数据可以用参数化合并，但不同逻辑必须拆分。

preconditions 放预备动作，steps 放有验证价值的具体操作。打开页面、登录这类动作属于前者，不要混入后者。

—


## 自动化示例

可自动化的用例推荐使用 pytest。

下面是一个完整的示例，展示精确断言的写法。

```python
import pytest


class TestUserRegister:
    """用户注册接口测试"""

    def test_register_success(self, api_client):
        """正向用例：正确填写注册信息"""
        phone = "13800138000"
        password = "Test@123456"

        response = api_client.register(phone, password)

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert "token" in response.json()["data"]

    @pytest.mark.parametrize("phone,password,expected_msg", [
        ("", "Test@123456", "手机号不能为空"),
        ("13800138000", "", "密码不能为空"),
        ("1380013800", "Test@123456", "手机号格式错误"),
    ])
    def test_register_field_validation(
        self, api_client, phone, password, expected_msg
    ):
        """反向校验：空值和格式错误"""
        response = api_client.register(phone, password)
        assert response.json()["code"] != 0
        assert expected_msg in response.json()["message"]
```

> 测试数据要独立于环境。使用专门的测试账号或动态生成数据，避免依赖特定数据库记录。

—


## 收尾

写好测试用例没有捷径。

先理解需求，再提取测试点，最后写用例。顺序不能乱。

七维度扫描法是系统化提取测试点的有效工具，尤其不要忽视权限、状态联动、异常容错这三个高价值维度。一条用例一个逻辑，是不可妥协的铁律。

掌握方法论之后，效率会越来越高。

—


**参考资料**

[1] pytest 官方文档: https://docs.pytest.org/
[2] Google Testing Blog — Test Case Design: https://testing.googleblog.com/
