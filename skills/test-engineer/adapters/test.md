# TEST 输出适配器

> **何时阅读**:阶段 3 输出 YAML 之前必读;调试转换问题或扩展新规则时必读。
> **核心动作**:Agent 用通用格式构思 → 落盘到中间文件 → 调用 `transform_yaml.py` 自动转换并校验。
> 参考 schema:`../test-test-case-skill/schema/test-case-schema.json`

## 使用方式(推荐:程序化转换)

阶段 3 默认走自动化流水线,**Agent 不需要手工套用下文 6 条规则**:

```bash
# 1. Agent 把通用格式 YAML 写入中间文件(裸 test_cases 列表即可)
#    例:.tmp/draft-login.yaml

# 2. 一键转换 + 校验,产物默认落在同名 .test.yaml
.venv-tools/bin/python $SKILL_ROOT/scripts/transform_yaml.py \
    .tmp/draft-login.yaml \
    -o testing-tm-cases/releases/<release>/login.yaml \
    --validate \
    --module "用户中心" --feature "登录"
```

脚本内置以下能力,失败会打印结构化错误并以非零退出码返回:
- 优先级降级(P3→P2)、type 映射、req_ref/trace 合并、顶层包装、字段白名单
- `--validate` 直接调用 jsonschema 检查,无需再单独跑 `validate_yaml.py`
- `--dry-run` 预览结果不落盘
- 目录递归(`--recursive`),产物自动落在同名 `.test.yaml`
- 已是 TEST 格式的 YAML 幂等通过(可放心反复运行)

下文 6 条规则保留作为**规则文档与 fallback 手册**:仅在脚本不可用、需要手工调试或扩展新规则时参考。

---

## 转换规则

### 规则 1：优先级降级

| 通用格式 | TEST 格式 | 说明 |
|----------|-----------|------|
| `P0` | `"P0"` | 不变，加引号 |
| `P1` | `"P1"` | 不变，加引号 |
| `P2` | `"P2"` | 不变，加引号 |
| `P3` | `"P2"` | **P3 不存于 TEST，降为 P2** |
| 空或无 | `"P2"` | 默认值 |

### 规则 2：type 枚举映射

| 通用 `type` | TEST `type` | 说明 |
|-------------|-------------|------|
| `functional` | `"functional"` | 直接映射 |
| `ui` | `"ui"` | 直接映射 |
| `security` | `"security"` | 直接映射 |
| `performance` | `"performance"` | 直接映射 |
| `accessibility` | `"accessibility"` | 直接映射 |
| `compatibility` | `"ui"` | 兼容性归入 UI |
| `usability` | `"ui"` | 可用性归入 UI（若偏无障碍则用 `"accessibility"`） |
| `observability` | `"functional"` | 可观测性归入功能，在 description 中注明 |

### 规则 3：字段合并

| 通用字段 | TEST 处理 | 示例 |
|----------|-----------|------|
| `req_ref` | **删除**，内容写入 `description` 首行 | `"追溯：Story-42"` |
| `trace` | **删除**，内容写入 `description` 首行 | `"追溯：Story-42 \| TP-03"` |
| `description` 已存在 | `req_ref`/`trace` **前插**到 `description` 开头 | `"追溯：Story-42\n原有描述"` |

### 规则 4：顶层包装

通用格式是裸列表，TEST 要求 `metadata` + `test_cases` 包装：

```yaml
# 通用格式
- id: TC_XXX_001
  title: ...
...

# TEST 格式
metadata:
  module: "<从文件所在目录推断模块名>"
  feature: "<从功能描述推断>"
  owner: <设为 "Tester"，或从上下文获取>
  last_reviewed: "<当天日期 YYYY-MM-DD>"
  tags: []

test_cases:
  - id: "TC_XXX_001"
    title: "..."
    ...
```

**metadata 字段填充规则**：
- `module`：若已知模块则填入，否则填 `"待确认"`
- `feature`：从用例功能场景概括
- `owner`：上下文有则填，否则 `"Tester"`
- `last_reviewed`：当天日期
- `tags`：如无全局标签填 `[]`

### 规则 5：字段值引号

| 通用格式 | TEST 格式 |
|----------|-----------|
| `priority: P0` | `priority: "P0"` |
| `type: functional` | `type: "functional"` |
| `id: TC_XXX_001` | `id: "TC_XXX_001"` |
| `title: ...` | `title: "..."` |
| `description: \|` | `description: "..."`（转为单行字符串） |
| `auto: false` | `auto: false`（boolean 不加引号） |

### 规则 6：字段白名单（删除多余额外字段）

TEST schema 的每个 test_case 对象 `additionalProperties: false`，**输出前必须删除**通用格式中存在但 TEST 不容许的字段：

**必须删除的字段**：`req_ref`、`trace`（内容已合并到 `description`）

**TEST 不支持但可保留在通用格式中的字段**（仅在无适配器时输出）：以上二者。

---

## 输出后校验

**推荐方式**:转换时直接加 `--validate`,程序内联校验:

```bash
.venv-tools/bin/python $SKILL_ROOT/scripts/transform_yaml.py <输入> -o <输出> --validate
```

**fallback**:对历史已存在的 TEST YAML 单独校验,使用:

```bash
.venv-tools/bin/python $SKILL_ROOT/scripts/validate_yaml.py <输出文件路径>
```

校验失败 → 对照本适配器规则排查 → 修复 → 重新校验,直到通过。

---

## 完整转换示例

### 通用格式（构思阶段）

```yaml
- id: TC_LOGIN_001
  title: 正确手机号和密码登录成功
  priority: P0
  type: functional
  req_ref: Story-42
  description: |
    验证已注册用户使用正确凭据可正常登录
  preconditions:
    - 用户已完成手机号注册
  steps:
    - 打开 App 首页
    - 输入已注册手机号
  expected_results:
    - 跳转至首页
  tags: [smoke]
  auto: false
```

### TEST 格式（输出阶段）

```yaml
metadata:
  module: "用户中心"
  feature: "手机号密码登录"
  owner: "Tester"
  last_reviewed: "2026-04-30"
  tags: []

test_cases:
  - id: "TC_LOGIN_001"
    title: "正确手机号和密码登录成功"
    priority: "P0"
    type: "functional"
    description: "追溯：Story-42\n验证已注册用户使用正确凭据可正常登录"
    preconditions:
      - "用户已完成手机号注册"
    steps:
      - "打开 App 首页"
      - "输入已注册手机号"
    expected_results:
      - "跳转至首页"
    tags: [smoke]
    auto: false
```
