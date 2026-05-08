# 默认输出适配器(test-engineer 通用格式)

> **何时阅读**:阶段 3 构思 YAML 时查阅(始终用此格式构思);阶段 3 输出前再读项目适配器(如 test.md)做转换。
> **覆盖范围**:原生 YAML 结构示例 / 完整字段列表 / 优先级说明 / 与项目适配器的关系。
> **可跳过条件**:已熟悉通用格式字段。

> 本文件定义 test-engineer 的**通用输出格式**。当前项目若未指定其他适配器,使用此格式。

## 原生 YAML 结构

test-engineer 原生输出为**裸 `test_cases` 列表**，无顶层 `metadata` 包装：

```yaml
- id: TC_MODULE_FUNC_001
  title: 被测对象 - 测试意图（具体行为）
  priority: P0
  type: functional
  req_ref: Story-42
  trace: TP-03
  description: |
    补充说明测试场景的业务背景
  preconditions:
    - 前置条件 1
  steps:
    - 操作步骤 1
  expected_results:
    - 预期结果 1
  tags: [模块标签, 场景标签]
  auto: false
```

## 完整字段列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | `TC_{模块}_{功能}_{三位序号}` |
| `title` | string | 是 | 不超过 40 字符 |
| `priority` | P0/P1/P2/P3 | 是 | **四**级优先级 |
| `type` | string | 是 | functional / ui / security / performance / compatibility / usability / accessibility / observability |
| `req_ref` | string | 否 | 需求追溯（Story ID） |
| `trace` | string | 否 | 测试点追溯（TP 编号） |
| `description` | string | 否 | 业务背景补充 |
| `preconditions` | string[] | 否 | 前置条件 |
| `steps` | string[] | 是 | 操作步骤 |
| `expected_results` | string[] | 是 | 预期结果 |
| `tags` | string[] | 否 | 标签 |
| `auto` | boolean | 否 | 默认 false |

## 优先级说明

| 等级 | 占比 | 定义 |
|------|------|------|
| P0 | 10%~15% | 核心流程、冒烟，fail 阻塞 |
| P1 | 30%~40% | 主要正向 + 重要异常 |
| P2 | 30%~40% | 次要功能、边界、UI |
| P3 | 10%~15% | 体验、极端边界、非功能 |

## 与项目适配器的关系

如果 `adapters/` 目录下存在项目适配器（如 `adapters/test.md`），Agent 在输出前**先按通用格式生成**，再按适配器规则**转换**后再输出。
