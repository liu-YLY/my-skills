# TEST 输出适配器

> **何时阅读**:阶段 3 输出 YAML 之前必读;调试转换问题或扩展新规则时必读。
> **核心动作**:Agent 用通用格式构思 → 落盘到中间文件 → 调用 `transform_yaml.py` 自动转换并校验。
> 参考 schema:`../test-test-case-skill/schema/test-case-schema.json`

## 使用方式(推荐:程序化转换)

阶段 3 默认走自动化流水线,**Agent 不需要手工套用下文规则**:

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

脚本能力:优先级降级(P3→P2)、type 映射、req_ref/trace 合并、顶层包装、字段白名单、引号格式;`--validate` 内联 jsonschema;`--dry-run` 预览;`--recursive` 目录递归;已是 TEST 格式幂等通过。

## 转换规则摘要（fallback 手册）

仅在脚本不可用时手工参考：

| # | 规则 | 通用→TEST |
|---|------|-----------|
| 1 | 优先级降级 | P0/P1/P2 不变加引号；P3→"P2"；空→"P2" |
| 2 | type 映射 | functional/ui/security/performance/accessibility 直接映射；compatibility→ui；usability→ui(偏无障碍→accessibility)；observability→functional |
| 3 | 字段合并 | req_ref/trace 删除，内容前插到 description 首行（格式："追溯：Story-42 \| TP-03\n原有描述"） |
| 4 | 顶层包装 | 裸列表→metadata+test_cases 包装；metadata: module/feature/owner/last_reviewed/tags |
| 5 | 字段值引号 | id/title/priority/type/description 加引号；auto(boolean)不加；preconditions/steps/expected_results 列表项加引号 |
| 6 | 字段白名单 | 删除 req_ref/trace（已合并）；additionalProperties:false |

## 输出后校验

```bash
# 推荐：转换时内联校验
.venv-tools/bin/python $SKILL_ROOT/scripts/transform_yaml.py <输入> -o <输出> --validate

# fallback：对历史 TEST YAML 单独校验
.venv-tools/bin/python $SKILL_ROOT/scripts/validate_yaml.py <输出文件路径>
```

校验失败 → 对照规则摘要排查 → 修复 → 重新校验。

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
