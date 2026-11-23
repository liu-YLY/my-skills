# 测试用例去说教化（v9.16.0）与结构性深瘦身实测验证报告

- **验证日期**：2026-11-23
- **关联计划**：[docs/superpowers/plans/2026-11-23-test-case-depreach-and-deep-slim-plan.md](../../superpowers/plans/2026-11-23-test-case-depreach-and-deep-slim-plan.md)
- **被测版本**：`test-case-engineer v9.16.0` + `review-checker-mcp v0.4.1`
- **评测等级**：`evaluated`（3 组独立干净上下文真实业务 PRD 端到端盲测 + 静态门禁全检 + `review-checker` 交叉校验）

---

## 一、上下文体积瘦身实测结果（对比 `main` 基线）

通过合并入口重复路由表、将低频知识（`bug-patterns.md`、`anti-patterns.md`、`traceability` 协同契约）从默认常驻主路径下沉为条件触发按需加载、删除与生成无关的生命周期章节并做无损表达脱水，全部指标均优于计划目标：

| 路径 / 模式 | `main` 基线（v9.15.0） | 本次实测（v9.16.0） | 新锁死门禁（`--target`） | 净减幅 |
|---|---:|---:|---:|---:|
| `entry`（`SKILL.md`） | 5,400 字 | **3,596 字** | 3,600 字 | **-33.4%** |
| `default`（默认生成主路径） | 36,990 字（9 文件） | **18,916 字（7 文件）** | 22,000 字 | **-48.9%** |
| `review`（已有用例评审） | 24,992 字 | **17,882 字** | 23,500 字 | **-28.4%** |
| `requirement-review`（PRD 评审） | 9,560 字 | **7,537 字** | 7,800 字 | **-21.2%** |
| 默认主路径常驻规范语句数 | 179 条 | **34 条** | — | **-81.0%** |

---

## 二、3 组独立干净上下文盲测结果（V-01 ～ V-03）

在未注入任何对话历史或额外提示词的前提下，并行启动 3 个独立 Subagent，仅提供 `SKILL.md` 入口与纯文本业务 PRD，验证按需加载路由、去说教规范、范围淘汰门与机器校验闭环：

| 场景编号 | 被测业务需求 | 按需文件加载表现 | 测试点产出（裁剪项） | 可执行用例（待确认单列） | `validate_cases.py` 结果 | 单条纯汉字均值 / 峰值（红线 ≤60） | 分号峰值（红线 ≤1） | `review-checker v0.4.1` 误诱导数 |
|---|---|---|---|---|---|---:|---:|---:|
| **V-01** | 企业账号注册邮箱激活链接有效期改造（生产 30m / 测试 5m，无全局时钟推进与邮件 Stub） | 按需命中 `failure-semantics.md`；未误读 `bug-patterns.md` | 10 个（8 落点 + 2 裁剪） | 10 条（+5 项待确认） | **0 error / 0 warn** | **21.9 / 34 字** | **1** | **0** |
| **V-02** | 待支付订单收银台防重复支付与第三方网关回调幂等（官方沙箱+充值接口，无故障注入器） | 按需命中 `failure-semantics.md`；未误读 `bug-patterns.md` | 13 个（10 落点 + 3 裁剪） | 12 条（+4 项待确认） | **首次即 0 error / 0 warn** | **21.2 / 34 字** | **1** | **0** |
| **V-03** | 开放平台新增 Webhook 订阅配置（3 角色、10 配额、HTTPS/SSRF 内网拦截、Secret 脱敏） | 精准命中安全/封顶特征按需加载 `bug-patterns.md` | 18 个（16 落点 + 2 裁剪） | 24 条（+4 项待确认） | **首次即 0 error / 0 warn** | **12.6 / 35 字** | **1** | **0** |
| **合计** | 3 个跨领域真实 PRD | 按需延迟加载 100% 符合路由预期 | 41 个（34 落点 + 7 裁剪） | **46 条**（+13 项待确认） | **全集 0 error / 0 warn** | **16.2 / 35 字** | **1** | **0** |

### 黄金锚点逐项核验结论

1. **零防作弊说教与免责自辩（`PREACH_NOISE = 0`）**：全集 46 条用例（228 条前置/步骤/结果语句）首次生成即无任何「服务可用/网络正常/无其他阻断」「测试期间不手工修改」「已记录快照/已回读」「不用其他原因代替本例命中」「由 UI 用例另验」等说教废话。
2. **零虚构夹具与零外置暗号表（`FICTIONAL_FIXTURE = 0`）**：
   - V-01 严格使用测试环境 5 分钟缩短参数，按第 4 分 45 秒（临界内）与第 5 分 10 秒（临界外）真实计时验证，未虚构可控全局时钟或隔离邮件网关 Stub；
   - V-02 严格通过测试充值接口与微信/支付宝官方沙箱构造前置状态，未虚构网关故障注入器，且无裸写数据库底层列名（`RAW_DB_COL = 0`）；
   - 全集所有账号、金额、URL 与密钥均在单条用例内自包含，未建立外部 `test-data` 暗号表。
3. **句法槽位与秒读精炼度达标（`RESULT_STEP_PREFIX = 0`、`SENTENCE_LEN = 0`）**：`业务结果` 零行首 `步骤 N：` 前缀（中间态全部规范落入 `关键检查点` 的 `步骤 N 后：`）；全集单条汉字均值仅 **16.2 字**、最大值 **35 字**（不到 60 字红线的 60%）。
4. **范围裁剪与未决问题隔离**：
   - V-01 未改动的注册表单校验、V-02 未改动的优惠券抵扣、V-03 未改动的历史投递日志与手动重放，均严格只保留 **1 条冒烟用例**；
   - V-03 中 PRD 明确未定义的「投递失败自动指数退避重试」被范围闸门直接裁剪为 **0 条用例**并附裁剪理由；
   - 13 项原文未决口径（如第 5 分钟整开闭区间、旧链接精确文案、172.16/IPv6 私网段口径、回调异常金额 HTTP 状态码）全部单列于文末「待确认场景」，未污染可执行用例集。

---

## 三、盲测现场捕获并闭环修复的 2 项历史摩擦点

真实盲测暴露了以往纯静态检查未能发现的两处文档模板与解析器不一致问题，已在本次迭代当场根治：

1. **`core.md` 测试点模板编号格式与 `validate_points.py` 冲突**：
   - **现象**：3 个 Subagent 首次运行 `validate_points.py` 均因照抄 `test-case-engineer-core.md` 模板示例中的纯数字编号 `| 1 |` 而触发 `TP_ID_FORMAT`（要求 `TP-序号` 格式），导致首轮必返工。
   - **修复**：已将 `test-case-engineer-core.md` 阶段 2 模板示例编号修正为 `| TP-01 |`。
2. **单行内联段落头（`**业务结果**: 内容`）被 `validate_cases.py` 漏解析**：
   - **现象**：V-01 首次采用 `writing-rules.md` 旧示例的单行写法 `**业务结果**: ...`（无行首 `-` 且未换行），既不命中 `META_RE` 也不命中要求行尾为空的旧 `SECTION_RE`，触发 `FIELD_REQUIRED` 误报。
   - **修复**：已将 `writing-rules.md` 示例统一为标准多行列表结构，同时升级 `validate_cases.py` 的 `SECTION_RE` 兼容同行冒号内联值并补齐 `test_inline_section_header_parsed_properly` 单测（单测总数增至 22 项全绿）。

---

## 四、确定性门禁最终验收清单

- `python3 scripts/check-version-sync.py`：`All version numbers are in sync.`
- `python3 scripts/check-skill-consistency.py`：`All skill consistency invariants hold.`
- `python3 scripts/check-md-links.py`：`All relative markdown links resolve.`
- `python3 scripts/check-knowledge-count.py`：`All skill knowledge references are intact.`
- `python3 scripts/check-project-inventory.py`：`Project inventory matches the current files.`
- `python3 scripts/check-context-budget.py --target`：全仓库 9 个 Skill 全部 `ok`
- `test_validate_cases.py`（22 项） / `test_validate_points.py` / `test_validate_requirement_review.py`：全部 `OK`
- `pytest`（`review-checker` + `test_repository_tools.py`）：`120 passed`
