# 阶段 3:编写测试用例

> **何时阅读**:进入阶段 3 时必读;无适配器场景下可跳过 3.0 与 3.4。
> **覆盖范围**:3.0 适配器检查 / 3.1 默认输出 functional / 3.2 输出格式选择 / 3.3 通用 YAML 模板 / 编写铁律 / 优先级标准 / 非功能用例追加模板 / 3.4 适配器转换流程(脚本化)。
> **关键约束**:默认仅输出 `type: functional`,触发条件命中才追加非功能;启用适配器时**必须**走 `transform_yaml.py` 而不是手工套用规则。
> **快速定位**:写功能用例 → 3.3;追加性能/安全/兼容用例 → 末尾「非功能用例追加模板」;转换 + 校验 → 3.4。

## 3.0 适配器检查(输出前必做)

在构思和输出 YAML 用例之前，**先检查 `adapters/` 目录**：

- **无适配器** → 用通用格式（`adapters/default.md`）直接输出，不校验
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

**按分层调整用例形态**：与 [knowledge/test-levels.md](knowledge/test-levels.md) 中「YAML 用例形态」表一致。

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
  description: |
    补充说明测试场景的业务背景
  preconditions:
    - 前置条件 1（明确环境、数据、用户状态）
    - 前置条件 2
  steps:
    - 操作步骤 1（祈使句，每步一个操作）
    - 操作步骤 2
  expected_results:
    - 预期结果 1（具体、可验证、引用实际文案）
    - 预期结果 2
  tags: [场景标签]
  auto: false
```

**如果启用了适配器**，按适配器规则转换为目标格式后再输出。
本仓库当前适配器：[adapters/test.md](adapters/test.md)

## 编写铁律

- **title**：`{被测对象} - {具体行为}`，不超过 40 字符，动宾结构
- **steps**：祈使句，每步一个操作，含具体输入值，建议 7 步以内
- **expected_results**：可直接判定 pass/fail，引用实际文案；**禁用模糊词**（完整清单见 [knowledge/test-standards.md](knowledge/test-standards.md)）
- **preconditions**：明确用户类型、数据状态、页面位置
- **id**：`TC_{模块}_{功能}_{三位序号}`
- **一个用例只覆盖单一测试逻辑**
- **需求追溯**：写入 `req_ref` 和 `trace` 字段（若适配器不支持则合并到 `description`）

## 优先级标准（通用）

- **P0**（10%~15%）：核心流程、支付/安全，fail 阻塞
- **P1**（30%~40%）：主要功能正向 + 重要异常
- **P2**（30%~40%）：次要功能、边界、UI
- **P3**（10%~15%）：体验、极端边界、非功能

划分遵循 [knowledge/test-standards.md](knowledge/test-standards.md) 三步法。
> 适配器可能降级（如 TEST 中 P3→P2），不影响构思阶段的划分。

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
