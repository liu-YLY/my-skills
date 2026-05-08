# 测试用例编写模式与范例

> **何时阅读**:阶段 3 写具体类型用例(CRUD/权限矩阵/联动/边界/表单)时按需查阅;阶段 4 评审用例时查末尾「评审清单」。
> **覆盖范围**:YAML 规范与 ID 命名 + 场景法(基本流/备选/异常) + 5 类常见模式模板(表单/CRUD/权限矩阵/联动/边界) + 字段级覆盖矩阵模板 + 元素级清单 + 非功能用例追加模板 + 评审 checklist。
> **可跳过条件**:本次用例形态简单,仅 happy path + 基础校验。
> **快速定位**:
> - 写权限差异用例 → 「权限/角色矩阵模式」
> - 写字段反向用例 → 「表单验证模式」+ 「字段级覆盖矩阵模板」
> - 写联动用例 → 「联动/状态依赖模式」
> - 用例评审 → 末尾「用例评审检查清单」

## YAML 测试用例规范

### 文件结构

```yaml
# 文件：releases/{版本目录}/{功能模块}.yaml
# 说明：{功能模块}功能测试用例集

metadata:
  module: 模块名称
  feature: 功能名称
  owner: name.surname
  last_reviewed: 2026-01-01
  tags: [模块标签, 功能标签]

test_cases:
  - id: TC_MODULE_FUNC_001
    title: 被测对象 - 测试场景简述
    priority: P0
    type: functional
    preconditions:
      - 前置条件
    steps:
      - 操作步骤
    expected_results:
      - 预期结果
    tags: [场景标签]
    auto: false
```

### ID 命名规范

```
TC_{模块缩写}_{功能缩写}_{三位序号}

示例：
TC_WEBHOOK_ADD_001     - Webhook 添加功能第 1 条
TC_WEBHOOK_LIST_001    - Webhook 列表功能第 1 条
TC_AUTH_LOGIN_001      - 认证模块登录第 1 条
TC_ORDER_PAY_001       - 订单支付第 1 条
```

### 字段编写规范

**title：** `{被测对象} - {测试意图}`
```yaml
# 好的
title: Endpoint URL 校验 - 为空时提示错误
title: Version 选择 - A类用户可选 V2~V5
title: Cancel 按钮 - 点击后不保存已填写内容

# 不好的
title: 测试 URL 输入
title: 验证版本功能
title: 取消按钮测试
```

**steps：** 使用祈使句，每步一个操作
```yaml
# 好的
steps:
  - 在 "Endpoint URL" 输入框中输入 `https://api.example.com/webhook`
  - 选择 Version 为 "Version 5.0"
  - 点击 "Add endpoint" 按钮

# 不好的
steps:
  - 输入 URL 并选择版本然后提交
```

**expected_results：** 具体、可验证
```yaml
# 好的
expected_results:
  - "Add endpoint" 按钮置灰不可点击
  - 输入框下方显示红色错误提示："Wrong URL format!"
  - 页面显示两个独立分组

# 不好的
expected_results:
  - 页面显示正常
  - 按钮状态正确
  - 提示信息正确
```

## 场景法（基本流/备选流/异常流）

场景法模拟用户真实使用路径，覆盖多步骤多功能组合。

### 三种流

| 流类型 | 定义 | 用例优先级 |
|--------|------|-----------|
| **基本流** | 用户按最正常路径完成操作（Happy Path） | P0 |
| **备选流** | 用户做出不同但合理的选择（如取消、修改、切换选项） | P1 |
| **异常流** | 输入错误、网络断开、超时等异常场景 | P1~P2 |

### 场景法用例设计步骤

1. **确定角色**：列出所有使用该功能的用户角色
2. **绘制基本流**：从入口到成功结束的最短正确路径
3. **识别备选流**：基本流每一步可能的分支（取消、回退、重选等）
4. **识别异常流**：每一步可能的错误输入、系统异常、中断
5. **一个场景 = 一条用例**：基本流 + 每条备选流/异常流各一条用例

### 示例

```
功能：添加 Webhook

基本流：打开弹窗 → 输入有效 URL → 选择 Version → 勾选 Status → 提交成功
  ↓
备选流 1：在基本流第 4 步点击 Cancel → 弹窗关闭，不保存
备选流 2：在基本流第 2 步修改 URL 后重新提交 → 以最终值提交成功
异常流 1：在基本流第 2 步输入无效 URL → 错误提示，按钮置灰
异常流 2：在基本流第 5 步网络断开 → 友好错误提示
异常流 3：在基本流第 5 步提交重复 URL → 提示 "Webhook already exist."
```

## 常见场景测试模式

### 表单验证模式

对表单的每个字段系统性覆盖：

```
字段 × 场景矩阵：
├── 必填字段
│   ├── 有效输入 → 提交成功
│   ├── 为空 → 错误提示
│   └── 格式错误 → 错误提示
├── 可选字段
│   ├── 有效输入 → 提交成功
│   ├── 为空 → 提交成功（字段忽略）
│   └── 超长输入 → 截断或提示
└── 按钮状态
    ├── 所有必填项满足 → 可点击
    └── 任一必填项缺失 → 置灰
```

### CRUD 模式

对资源的增删改查操作覆盖：

```
Create (创建)：
  - 正常创建 → 返回 201，列表新增
  - 必填缺失 → 400 错误
  - 重复创建 → 409 冲突
  - 超出上限 → 业务限制提示

Read (查询)：
  - 查询存在的资源 → 返回 200 + 数据
  - 查询不存在的资源 → 返回 404
  - 列表查询 → 分页、排序、筛选

Update (更新)：
  - 正常更新 → 200，数据变更
  - 更新不存在的资源 → 404
  - 无权更新 → 403
  - 并发更新 → 冲突处理

Delete (删除)：
  - 正常删除 → 204，列表移除
  - 删除不存在的资源 → 404
  - 有关联数据 → 级联或阻止
```

### 权限/角色矩阵模式

```yaml
# 对每个角色 × 功能组合覆盖
# 示例：用户类型决定可用版本

# A 类用户
- id: TC_WEBHOOK_ADD_006
  title: Version 选择 - A类用户（原V2/V3客户）可选 V2~V5
  priority: P0
  preconditions:
    - 当前用户被标记为 A 类客户
  steps:
    - 打开 "Add webhook" 弹窗
    - 点击 "Version" 下拉框
  expected_results:
    - 下拉选项包含：Version 2.0, Version 3.0, Version 4.0, Version 5.0

# B 类用户
- id: TC_WEBHOOK_ADD_007
  title: Version 选择 - B类用户（上线前注册）可选 V4~V5

# C 类用户
- id: TC_WEBHOOK_ADD_008
  title: Version 选择 - C类用户（新用户）仅可选 V5
```

### 联动/状态依赖模式

选项 A 的值影响选项 B 的可选范围：

```yaml
# Version → 可用 Status 联动
- id: TC_WEBHOOK_ADD_009
  title: Status 选择 - v5 版本显示两组新状态
  preconditions:
    - Version 选择为 "Version 5.0"
  steps:
    - 查看状态选择区域
  expected_results:
    - 页面显示两个独立分组：
      1. "系统子状态" 组包含 N 个选项
      2. "轨迹主状态" 组包含 N 个选项
    - 不显示旧版状态
```

### 边界/限制模式

```yaml
# 数量上限
- id: TC_WEBHOOK_ADD_016
  title: 验证用户最多加 4 个 webhook
  preconditions:
    - 用户已创建 4 个 Webhook
  steps:
    - 点击 "Add endpoint" 按钮
  expected_results:
    - 弹窗显示提示信息："Maximum allow 4 webhook URL."

# 重复校验
- id: TC_WEBHOOK_ADD_017
  title: 验证用户添加重复 URL 的 webhook
  preconditions:
    - 已存在 URL 为 `https://api.example.com/webhook` 的 Webhook
  steps:
    - 输入相同 URL 并提交
  expected_results:
    - 表单提交失败，显示错误："Webhook already exist."
```

## 字段级覆盖矩阵模板

对每个页面/表单，逐字段展开完整覆盖：

```markdown
### 字段覆盖矩阵：{页面名称}

| 字段名 | 必填 | 有效输入 | 空值 | 格式错误 | 边界值 | 特殊字符 | 用例ID |
|--------|------|----------|------|----------|--------|----------|--------|
| Endpoint URL | 是 | https://... | 空 → 错误提示 | 无协议头 | 最大长度 | 含空格/中文 | 001-005 |
| Description | 否 | 正常文本 | 空 → 通过 | N/A | 100字符上限 | emoji/html | 006-008 |
| Version | 是 | 角色对应选项 | N/A | N/A | N/A | N/A | 009-011 |
```

确保每个字段在矩阵中都有对应行，不遗漏。

## 页面/功能级覆盖清单

对每个页面，逐元素扫描：

```markdown
### 元素覆盖清单：{页面名称}

**输入类元素**：
- [ ] 字段 A → 用例 001-005
- [ ] 字段 B → 用例 006-008

**操作类元素**：
- [ ] 提交按钮 → 用例 015（联动状态）
- [ ] 取消按钮 → 用例 014
- [ ] 链接/跳转 → 用例 013

**展示类元素**：
- [ ] 错误提示文案 → 分布在各反向用例中
- [ ] 列表/选项变化 → 用例 009-012

**遗漏检查**：
- [ ] 是否有隐藏的条件展示（如某选项仅特定条件可见）？
- [ ] 是否有 loading/disabled 等中间状态？
- [ ] 是否有刷新/返回后的状态恢复？
```

## 非功能测试用例追加规则

默认只输出功能测试用例。当以下条件满足时，在功能测试用例**之后**追加对应类型：

### 性能测试（用户要求 或 需求提到性能指标）

```yaml
- id: TC_MODULE_PERF_001
  title: 功能名 - 正常负载下响应时间
  priority: P1
  type: performance
  preconditions:
    - 系统处于正常运行状态
    - 并发用户数：N
  steps:
    - 执行目标操作 N 次
    - 记录每次响应时间
  expected_results:
    - 平均响应时间 < X ms
    - P99 响应时间 < Y ms
    - 无超时或错误响应
  tags: [performance, load]
  auto: false
```

### 安全测试（涉及认证/授权/敏感数据）

```yaml
- id: TC_MODULE_SEC_001
  title: 功能名 - 未认证用户访问受保护接口
  priority: P0
  type: security
  preconditions:
    - 用户未登录或 token 已过期
  steps:
    - 直接请求受保护的 API 端点
  expected_results:
    - 返回 401 Unauthorized
    - 不返回任何业务数据
  tags: [security, auth]
  auto: false
```

### 兼容性测试（需求提到多端/多浏览器）

```yaml
- id: TC_MODULE_COMPAT_001
  title: 功能名 - Chrome/Firefox/Safari 下表单渲染一致
  priority: P2
  type: compatibility
  preconditions:
    - 分别在 Chrome/Firefox/Safari 最新版本中打开页面
  steps:
    - 检查页面布局和元素位置
    - 执行核心操作流程
  expected_results:
    - 三个浏览器中布局一致，无错位
    - 核心功能均可正常使用
  tags: [compatibility, browser]
  auto: false
```

## 用例评审检查清单

**覆盖完整性**：
- [ ] 每条用例 title 清晰表达测试意图
- [ ] 字段覆盖矩阵中每个字段均有用例
- [ ] 7 大维度（正向/反向/权限/联动/边界/交互/异常）均已扫描
- [ ] 不同角色/权限组合全部覆盖
- [ ] 联动依赖关系全部覆盖
- [ ] 取消/返回/刷新等辅助操作已覆盖

**可执行性**：
- [ ] preconditions 充分且可操作
- [ ] steps 可独立执行（不依赖其他用例结果）
- [ ] steps 包含具体输入值和操作对象
- [ ] expected_results 具体可验证（无"正常""正确"等模糊词）
- [ ] expected_results 引用了实际 UI 文案或接口返回

**规范性**：
- [ ] priority 符合业务重要性
- [ ] ID 符合命名规范且无重复
- [ ] tags 便于后续筛选
- [ ] 需要追加非功能用例的场景已识别
