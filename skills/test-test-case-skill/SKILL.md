---
name: TEST Test Case Generator
description: Generate structured, standardized YAML test cases for TEST's lightweight test management system.
---

## Overview
This Skill helps testers and engineers at TEST create consistent, review-ready YAML test cases that follow the team's official specification. It ensures all required fields (ID, steps, expected results, priority, etc.) are present and formatted correctly for Git-based test case management.

The canonical structure and validation rules are defined in JSON Schema: **`schema/test-case-schema.json`** (Draft 07). Generated YAML must conform to that schema.

Use this Skill whenever you need to:
- Draft new functional test cases
- Convert manual test steps into YAML format
- Validate or fix existing YAML test cases
- Ensure compliance with TEST's test case schema

## Input Format
Provide one of the following:
- A natural language description of a test scenario (e.g., "User logs in with wrong password")
- An incomplete or malformed YAML test case
- A list of test steps and expected outcomes

## Output Format
A complete, valid YAML snippet that can be directly saved into the `test-cases/` repository, including:
- Proper **`metadata`** section (not `meta`; see schema)
- Correctly formatted `test_cases` array
- Valid `id`, `title`, `steps`, `expected_results`, `priority`, `type`, and optional `tags` / `auto`

## Schema: Root Document

| Constraint | Value |
|------------|--------|
| Top-level keys | Only **`metadata`** and **`test_cases`** (`additionalProperties`: false) |
| Required | `metadata`, `test_cases` |

## Schema: `metadata`

| Field | Required | Type / format | Notes |
|-------|----------|----------------|-------|
| `module` | yes | string | 所属大模块 |
| `feature` | yes | string | 当前文件聚焦功能 |
| `owner` | yes | string | 负责人（英文名） |
| `last_reviewed` | yes | string, **date** | `YYYY-MM-DD` |
| `tags` | no | string[] | 全局标签 |
| Other keys | — | — | **Not allowed** (`additionalProperties`: false) |

## Schema: `test_cases`

- Array with **at least one** item (`minItems`: 1).

### Each test case object

| Field | Required | Type / constraint | Notes |
|-------|----------|-------------------|--------|
| `id` | yes | string, pattern | `^TC_[A-Z0-9_]{3,}_[0-9]{3}$` — 全局唯一；`TC_<功能缩写>_<三位序号>` |
| `title` | yes | string | 简洁、动词开头的标题 |
| `priority` | yes | enum | `P0` \| `P1` \| `P2` |
| `type` | yes | enum | `functional` \| `ui` \| `security` \| `performance` \| `accessibility` |
| `steps` | yes | string[] | **≥1** step; each step **non-empty** string |
| `expected_results` | yes | string[] | **≥1** item; each **non-empty** string |
| `description` | no | string | 补充说明 |
| `preconditions` | no | string[] | 执行前提 |
| `tags` | no | string[] | 用例级标签 |
| `auto` | no | boolean | 是否计划自动化；**default** `false` |
| Other keys | — | — | **Not allowed** (`additionalProperties`: false) |

## Example Usage

### Input:
> Write a P0 test case for successful user login with phone and password.

### Output:

```yaml
metadata:
  module: "用户中心"
  feature: "手机号密码登录"
  owner: "Tester"
  last_reviewed: "2026-01-30"
  tags: [auth, mobile]

test_cases:
  - id: "TC_LOGIN_001"
    title: "正确手机号和密码登录成功"
    description: "验证已注册用户使用正确凭据可正常登录"
    priority: "P0"
    type: "functional"
    preconditions:
      - "用户已完成手机号注册"
      - "网络连接正常"
    steps:
      - "打开 App 首页"
      - "点击「登录」按钮"
      - "输入已注册手机号"
      - "输入正确密码"
      - "点击「登录」按钮"
    expected_results:
      - "跳转至首页"
      - "顶部导航栏显示用户名"
      - "本地存储包含有效 token"
    tags: [smoke, happy-path]
    auto: false