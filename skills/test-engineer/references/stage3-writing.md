# 阶段 3:编写测试用例

> **何时阅读**:进入阶段 3 时必读;无适配器场景下可跳过 3.0 与 3.4。
> **覆盖范围**:3.0 适配器检查 / 3.0a AI 生成模式(默认) / 3.0b 人工编写模式(备选) / 3.1 默认输出 functional / 3.2 输出格式选择 / 3.3 通用 YAML 模板 / 编写与审核铁律 / 优先级标准 / 非功能用例追加模板 / 3.4 适配器转换流程(脚本化)。
> **关键约束**:默认走 AI 生成模式;仅输出 `type: functional`,触发条件命中才追加非功能;启用适配器时**必须**走 `transform_yaml.py` 而不是手工套用规则。
> **快速定位**:AI 生成用例 → 3.0a;人工编写 → 3.0b;写功能用例 → 3.3;追加性能/安全/兼容用例 → 末尾「非功能用例追加模板」;转换 + 校验 → 3.4。

## 3.0a AI 生成模式（默认）

**默认走 AI 生成模式**。将阶段 1 的需求理解 + 阶段 2 的测试点清单作为输入，使用结构化 Prompt 让 AI 生成基础用例，人工负责审核、修正和补充。

**流程**：
1. 读取 [knowledge/prompt-strategy.md](../knowledge/prompt-strategy.md) 中的结构化提示词模板
2. 将需求理解 + 测试点清单填入 Prompt 模板
3. AI 生成 70%-90% 的基础用例（正常场景 + 边界值 + 异常场景）
4. **人工审核**：检查业务逻辑准确性、补充领域特有边界条件、验证优先级合理性
5. 人工补充 AI 遗漏的复杂业务逻辑用例
6. 进入 3.0 适配器检查

**AI 生成的用例标记** `source: ai-generated`，人工补充的标记 `source: manual`。

**审核重点**：
- 业务逻辑是否准确（AI 可能误解需求细节）
- 领域特有边界条件是否覆盖（AI 通用性强但领域深度不足）
- 优先级是否合理（AI 倾向均匀分配，可能忽略核心路径）
- steps 是否可直接执行（AI 可能生成抽象描述而非具体操作）

## 3.0b 人工编写模式（备选）

以下场景使用人工编写模式：
- 用户明确要求人工编写
- 功能极简（< 5 条用例）
- 需求高度领域特化，AI 生成质量不达标

人工编写时跳过 Prompt 调用，直接按 3.3 通用 YAML 模板编写。

## 3.0 适配器检查(输出前必做)

在构思和输出 YAML 用例之前，**先检查 `adapters/` 目录**：

- **无适配器** → 用本文件 3.3 节通用格式直接输出，不校验
- **有适配器**（如 `adapters/test.md`）→ 构思用通用格式，转换用适配器规则，输出后校验

## 3.1 默认输出功能测试用例

除非用户明确要求或需求内容明显涉及以下类型，否则**只输出功能测试用例（`type: functional`）**：

| 额外类型 | 触发条件 | 通用 `type` |
|----------|----------|------------|
| 性能测试 | 需求提到响应时间、并发量、吞吐量要求 | `performance` |
| 安全测试 | 涉及认证、授权、敏感数据、支付 | `security` |
| 兼容性测试 | 需求提到多浏览器、多设备、多系统版本 | `compatibility` |
| 可用性/UI测试 | 需求有明确的设计稿或交互规范 | `usability` 或 `ui` |
| 无障碍测试 | 需求有明确的无障碍规范 | `accessibility` |
| 可观测性 | 要求验收日志/指标/告警 | `observability` |

当需要额外类型时，在功能测试用例之后**独立成组**追加。

> **适配器映射**：若启用了项目适配器，type 按适配器规则映射（如 TEST 中 `compatibility`/`usability` → `ui`，`observability` → `functional`）。

**按分层调整用例形态**：与 [knowledge/test-levels.md](../knowledge/test-levels.md) 中「YAML 用例形态」表一致。

## 3.2 输出格式

- **默认**：通用 YAML + 适配器转换
- **用户指定其他格式时**：将同一批测试意图迁移为 **Gherkin** 或 **Markdown 表格**

## 3.3 通用 YAML 格式（构思阶段）

```yaml
- id: TC_MODULE_FUNC_001
  title: 被测对象 - 测试意图（具体行为）
  priority: P0
  type: functional
  req_ref: Story-42
  trace: TP-03
  source: ai-generated  # ai-generated | manual | ai-reviewed
  description: |
    补充说明测试场景的业务背景
  preconditions:
    - 已登录为 A 类用户（预备动作放这里）
    - 已打开 "Add webhook" 弹窗（预备动作放这里）
  steps:
    - 操作步骤 1（祈使句，一步一动作）          # ← 对应 expected_results[0]
    - 操作步骤 2                                # ← 对应 expected_results[1]
  expected_results:
    - 预期结果 1（步骤1完成后立即可观察的结果）  # ← 对应 steps[0]
    - 预期结果 2（步骤2完成后立即可观察的结果）  # ← 对应 steps[1]
  tags: [场景标签]
  auto: false
```

**如果启用了适配器**，按适配器规则转换为目标格式后再输出。
本仓库当前适配器：[adapters/test.md](adapters/test.md)

### 字段列表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | `TC_{模块}_{功能}_{三位序号}` |
| `title` | string | 是 | 不超过 40 字符，动宾结构 |
| `priority` | P0/P1/P2/P3 | 是 | 定义与比例见 [test-standards.md](../knowledge/test-standards.md) |
| `type` | string | 是 | functional / ui / security / performance / compatibility / usability / accessibility / observability |
| `req_ref` | string | 否 | 需求追溯（Story ID） |
| `trace` | string | 否 | 测试点追溯（TP 编号） |
| `source` | string | 否 | 用例来源：ai-generated / manual / ai-reviewed |
| `description` | string | 否 | 业务背景补充 |
| `preconditions` | string[] | 否 | 前置条件 |
| `steps` | string[] | 是 | 操作步骤 |
| `expected_results` | string[] | 是 | 预期结果 |
| `tags` | string[] | 否 | 标签 |
| `auto` | boolean | 否 | 默认 false |

## 编写与审核铁律

### 审核规则（AI 生成模式必做）

AI 生成的用例**必须经过人工审核**才能进入 Active 状态：

| 审核项 | 检查内容 | 不通过处理 |
|--------|----------|-----------|
| 业务逻辑 | AI 是否正确理解了业务规则 | 修正 steps/expected_results |
| 领域边界 | 是否遗漏了领域特有的边界条件 | 补充用例，标记 source: manual |
| 优先级 | P0/P1 是否覆盖了核心路径 | 调整 priority |
| 可执行性 | steps 是否具体到可直接执行 | 补充具体值、元素名 |
| 模糊词 | expected_results 是否含模糊词 | 替换为具体描述 |

**审核后**，将 AI 生成用例的 `source` 从 `ai-generated` 更新为 `ai-reviewed`。

### 测试点→用例映射规则

| 场景 | 操作 | 示例 |
|------|------|------|
| 同一流程，不同测试数据 | **合并为 1 条用例**，数据参数化 | URL 格式校验：有效/无效/空值 → 1 条用例 3 组数据 |
| 不同前置条件 | **拆分为独立用例** | A 类用户 vs C 类用户 → 2 条用例 |
| 不同预期结果 | **拆分为独立用例** | 提交成功 vs 重复提交 → 2 条用例 |
| 不同测试逻辑 | **拆分为独立用例** | 正向提交 vs 边界超限 → 2 条用例 |
| 同一字段多类校验 | **按类拆分**，每类 1 条 | 必填校验 1 条 + 格式校验 1 条 + 边界校验 1 条 |

**核心原则**：一条用例只验证一个测试逻辑；同一逻辑不同数据可合并；不同逻辑必须拆分。

- **title**：`{被测对象} - {具体行为}`，不超过 40 字符，动宾结构
- **steps**：祈使句，每步一个操作，含具体输入值，建议 7 步以内
- **expected_results**：可直接判定 pass/fail，引用实际文案；**禁用模糊词**（完整清单见 [knowledge/test-standards.md](../knowledge/test-standards.md)）；**必须覆盖三层**：
  - **主观察**：用户直接可见的结果（UI 文案、页面状态、跳转）
  - **副作用**：操作触发的附带效果（通知发送、缓存更新、日志写入）
  - **状态验证**：后端数据/状态变更（DB 记录、资源状态、对账结果）
- **preconditions**：明确用户类型、数据状态、页面位置
- **id**：`TC_{模块}_{功能}_{三位序号}`
- **一个用例只覆盖单一测试逻辑**
- **需求追溯**：写入 `req_ref` 和 `trace` 字段（若适配器不支持则合并到 `description`）
- **用例来源**：写入 `source` 字段标记用例来源（ai-generated / manual / ai-reviewed），便于效率度量

### steps ↔ expected_results 一一对应（强制）

**`steps[N]` 和 `expected_results[N]` 数量必须一致**，每步操作后立即写出对应的预期结果，实现"一步一验"。

| 正例（1步→1结果） | 反例（2步→1结果） | 问题诊断 |
|------|------|------|
| step1: 在 URL 输入框留空 / step2: 点击提交 → result1: 输入框下方显示红色提示"必填" / result2: 弹窗未关闭，提交失败 | step1: 在 URL 输入框留空 / step2: 点击提交 → result1: 提交失败，提示必填 | **无法区分**是留空触发的校验还是点击提交触发的校验；若步骤1就报错则步骤2不执行，但预期结果只有一个 |
| step1: 输入正确的手机号和密码 → result1: 登录按钮变为可点击状态 | step1: 打开 App 首页 / step2: 输入已注册手机号 → result1: 跳转至首页 | 打开首页是预备动作不应放在 steps；输完手机号还没点登录就断言跳转 |

**处理方式**：
1. **预备动作上移**：将"打开页面、登录、进入菜单"等无验证价值的预备动作移到 **preconditions**
2. **合并相邻**：若预备动作必须留在 steps（操作链不可拆分），与第一个产生结果的动作合并为一步，如 `"打开 Add webhook 弹窗，在 URL 输入框中输入 'https://...'"`
3. **按步分层分配验证**：三步验证（主观察/副作用/状态验证）可分步承载，不要求每一步都覆盖三层

**因果性约束**：`expected_results[N]` 必须是 **`steps[N]` 单独执行后立即产生的可观察变化**，不能是 `steps[N+1]` 或其他后序步骤的结果。如果某步无可见变化，说明该步骤:
- 是纯预备动作 → 移入 preconditions
- 粒度太细 → 与相邻步骤合并

**自检**：写完用例后，逐行读 `steps[N]`，问自己「仅执行这步操作后，我能看到什么？」，写下答案即为 `expected_results[N]`。再检查：`expected_results[N]` 中是否出现了 `steps[N]` 之后的元素名或依赖后续步骤的现象——出现即错位。

## 优先级与类型

优先级定义、比例、三步法划分见 [knowledge/test-standards.md](../knowledge/test-standards.md)；type 枚举见上方字段列表。构思阶段用通用 P0-P3 + 完整 type；适配器可能降级（如 TEST 中 P3→P2），不影响构思。

## 非功能用例追加模板（通用格式）

### 性能测试

```yaml
- id: TC_MODULE_PERF_001
  title: 功能名 - 正常负载下响应时间
  priority: P1
  type: performance
  req_ref: PRD §5
  preconditions:
    - 系统处于正常状态
  steps:
    - 执行目标操作 N 次
    - 记录每次响应时间
  expected_results:
    - 平均响应时间 < X ms
    - P99 响应时间 < Y ms
  tags: [performance, load]
  auto: false
```

### 安全测试

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

### 兼容性测试

```yaml
- id: TC_MODULE_COMPAT_001
  title: 功能名 - Chrome/Firefox/Safari 下渲染一致
  priority: P2
  type: compatibility
  preconditions:
    - 分别在 Chrome/Firefox/Safari 最新版中打开
  steps:
    - 检查页面布局和元素位置
    - 执行核心操作流程
  expected_results:
    - 三个浏览器布局一致，无错位
    - 核心功能均可正常使用
  tags: [compatibility, browser]
  auto: false
```

---

## 3.4 适配器转换与校验(若有适配器)

当 `adapters/` 目录下存在项目适配器时,**优先使用程序化转换**,而不是手工套用规则:

### 推荐流程(自动化)

1. **构思用通用格式**(如上文模板),把裸 `test_cases` 列表写入中间草稿文件
   (例:`.tmp/draft.yaml`)
2. **一键转换 + 校验**:

```bash
.venv-tools/bin/python $SKILL_ROOT/scripts/transform_yaml.py \
    .tmp/draft.yaml \
    -o testing-tm-cases/releases/<release>/<feature>.yaml \
    --validate \
    --module "<模块名>" --feature "<功能名>"
```

脚本内置全部 6 条 TEST 规则:优先级降级、type 映射、req_ref/trace 合并、顶层包装、字段白名单、引号格式;`--validate` 内联调用 jsonschema。

3. **校验通过** → 进入阶段 4
4. **校验失败** → 阅读 stderr 中的结构化错误信息(`[路径] 期望/实际`),对照 [adapters/test.md](../adapters/test.md) 规则修复草稿,重新跑脚本直到通过

### Fallback 流程(脚本不可用时)

仅当脚本因依赖问题无法运行时,才退回到手工流程:逐条读 [adapters/test.md](../adapters/test.md) 套用规则,然后单独跑 `validate_yaml.py` 校验。
