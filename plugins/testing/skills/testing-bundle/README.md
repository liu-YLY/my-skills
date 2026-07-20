# Testing Bundle Skill

> 测试能力 bundle 入口 v3.0.0：统一路由到 5 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer）。

## 简介

Testing Bundle 是一个元 skill（meta skill），本身不实现具体测试能力，而是作为测试能力的统一入口，根据用户意图自动路由到对应的子 skill。

### 为什么需要 Bundle

拆分后存在 5 个独立 skill：
- `test-strategy-engineer`：专注项目级测试策略
- `test-case-engineer`：专注功能用例生成
- `performance-test-engineer`：专注性能测试方案与瓶颈定位
- `bug-analyzer`：专注功能缺陷根因
- `state-machine-test-engineer`：专注状态机驱动的状态型需求测试（订单/审批/工单/会员等生命周期）

用户提出"测试相关"请求时，可能需要其中任何一个，也可能多个协同。Bundle 解决三个问题：
1. **统一入口**：用户无需预先判断该用哪个 skill
2. **混合意图协同**：自动编排多 skill 协同流程（5 条混合意图链）
3. **依赖关系管理**：显式声明 bug-analyzer 对 test-case-engineer 知识库的依赖、state-machine-test-engineer 对可选 MCP Server 的依赖

## 子 skill 说明

| 子 skill | 职责 | 核心工作流 |
|---------|------|----------|
| [test-strategy-engineer](../test-strategy-engineer/) | 项目级测试策略 | 五阶段：项目特征 → 风险矩阵 → 分层 → 范围准入准出 →（可选）资源附录 |
| [test-case-engineer](../test-case-engineer/) | 功能用例生成 | 四阶段：理解需求 → 提取测试点 → 编写用例 → 自检补全 |
| [performance-test-engineer](../performance-test-engineer/) | 性能测试方案+瓶颈定位 | 四阶段：需求理解 → 场景设计 → 瓶颈定位 → 转交判断 |
| [bug-analyzer](../bug-analyzer/) | 功能缺陷根因 | 五步定位法：复现 → 隔离 → 定位 → 验证 → 报告 |
| [state-machine-test-engineer](../state-machine-test-engineer/) | 状态机建模+场景穷举 | 五阶段：状态型需求识别 → 状态机建模 → 完整性检查 → 10类场景穷举 →（可选）MCP 增强 |

## 路由规则

Bundle 根据用户意图自动路由：

| 用户意图 | 路由到 |
|---------|--------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出 | test-strategy-engineer |
| 生成/评审测试用例、需求分析、单功能测试策略 | test-case-engineer |
| 性能测试、负载测试、TPS、响应时间、瓶颈 | performance-test-engineer |
| Bug 根因分析、缺陷定位、5 Whys、防御性用例反推 | bug-analyzer |
| 状态机、状态流转、状态转换、生命周期、非法跳转、幂等、并发冲突、消息乱序、终态吸收 | state-machine-test-engineer |
| 混合意图（5 条链） | 见 SKILL.md 混合意图链 |
| 意图不明确 | 追问用户 |

**5 条混合意图链**：
1. Bug 分析 + 用例生成（bug-analyzer → case-engineer）
2. 测试策略 + 分层用例（strategy → case-engineer）
3. 性能测试 + 瓶颈定位（performance 内部完成）
4. 性能瓶颈 + 代码缺陷（performance → bug-analyzer）
5. **状态机建模 + 用例生成**（state-machine → case-engineer）← v3.0.0 新增

## 安装方式

### 方式 1：整体安装（推荐）

```
skills/
├── testing-bundle/              ← 本 skill（路由入口）
├── test-strategy-engineer/      ← 子 skill（项目级策略）
├── test-case-engineer/          ← 子 skill（用例生成）
├── performance-test-engineer/   ← 子 skill（性能测试）
├── bug-analyzer/                ← 子 skill（Bug 分析）
└── state-machine-test-engineer/ ← 子 skill（状态机测试，v3.0.0 新增）
```

获得完整测试能力，bundle 自动路由，无需用户判断该用哪个子 skill。

### 方式 2：按需安装

- 只需项目级策略 → 仅安装 `test-strategy-engineer`
- 只需用例生成 → 仅安装 `test-case-engineer`
- 只需性能测试 → 仅安装 `performance-test-engineer`
- 只需 Bug 分析 → 仅安装 `bug-analyzer`（缺陷模式库引用会降级）
- 只需状态机测试 → 仅安装 `state-machine-test-engineer`（可选再装配套 MCP Server 进入增强模式）
- 不安装 `testing-bundle` 时，用户需自行判断该用哪个子 skill

## 知识库依赖

- `bug-analyzer` 依赖 `test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库），通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- `test-strategy-engineer` 与 `performance-test-engineer` 的知识库独立，不与其他子 skill 共享
- `state-machine-test-engineer` 知识库独立（含 4 个行业状态机模板：订单退款/审批流/会员/工单）；可选调用 `state-machine-testing-mcp` Server 做 Schema 校验与可视化，未安装时降级为纯 LLM 推理

## 使用示例

### 示例 1：自动路由到用例生成
```
用户：我有一个登录功能需要测试...
→ bundle 路由到 test-case-engineer
 输出测试用例
```

### 示例 2：自动路由到 Bug 分析
```
用户：线上重复扣款 Bug 帮我分析根因
→ bundle 路由到 bug-analyzer
 输出根因分析报告
```

### 示例 3：混合意图协同（Bug + 用例，链 1）
```
用户：分析这个 Bug 并补充测试用例
→ bundle 路由到 bug-analyzer（输出防御性测试点清单）
 转交 test-case-engineer（基于清单生成完整用例）
 输出根因分析 + 完整用例
```

### 示例 4：自动路由到测试策略
```
用户：新项目要制定测试策略，包含分层和准入准出
→ bundle 路由到 test-strategy-engineer
 输出项目级测试策略（分层 + 风险矩阵 + 准入准出）
```

### 示例 5：自动路由到性能测试
```
用户：支付接口要做性能测试，目标 TPS 2000
→ bundle 路由到 performance-test-engineer
 输出性能测试方案 + 场景设计 + 瓶颈定位流程
```

### 示例 6：自动路由到状态机测试（v3.0.0 新增）
```
用户：订单退款流程要做测试，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败
→ bundle 路由到 state-machine-test-engineer
 输出状态机模型 + 场景清单（含依据类型标注，未说明的退款失败恢复路径标"待确认"）
```

### 示例 7：状态机 + 用例协同（链 5，v3.0.0 新增）
```
用户：为订单退款流程设计状态机测试场景，并生成完整测试用例
→ bundle 路由到 state-machine-test-engineer（输出状态机模型 + 场景清单）
🔴 CHECKPOINT 用户确认后
 转交 test-case-engineer（基于场景清单生成完整用例）
 输出状态机模型 + 场景清单 + 完整测试用例
```

## 文件结构

```
testing-bundle/
├── SKILL.md           # 入口（路由规则 + 协同流程）
├── README.md          # 本说明文档
├── CHANGELOG.md       # 版本变更记录
└── test-prompts.json  # 路由验证 prompt
```

## 反例与黑名单

- ❌ bundle 层重复实现子 skill 的能力
- ❌ 不判断意图直接调用某个子 skill
- ❌ 只装 bundle 不装子 skill（bundle 无法独立完成任何任务）
- ❌ 路由时不传递上下文
- ❌ 把性能问题路由到 bug-analyzer（应路由到 performance-test-engineer）
- ❌ 把项目级策略路由到 test-case-engineer（应路由到 test-strategy-engineer）
- ❌ 把通用功能用例路由到 state-machine-test-engineer（应路由到 test-case-engineer，仅当含明确状态/生命周期信号才路由到 state-machine）

## 版本历史

- v1.0.0: 初始版本，2-skill 路由
- v2.0.0: 扩展为 4-skill 路由（+ test-strategy-engineer + performance-test-engineer），breaking change
- v3.0.0: 扩展为 5-skill 路由（+ state-machine-test-engineer），新增链 5（状态机+用例协同），breaking change

详细变更见 [CHANGELOG.md](CHANGELOG.md)。

---

**相关文档**：
- [SKILL.md](SKILL.md) - 完整路由规则与协同流程
- [CHANGELOG.md](CHANGELOG.md) - 版本变更记录
- [test-strategy-engineer](../test-strategy-engineer/) - 项目级测试策略子 skill
- [test-case-engineer](../test-case-engineer/) - 功能用例生成子 skill
- [performance-test-engineer](../performance-test-engineer/) - 性能测试子 skill
- [bug-analyzer](../bug-analyzer/) - 功能缺陷根因分析子 skill
- [state-machine-test-engineer](../state-machine-test-engineer/) - 状态机测试子 skill（v3.0.0 新增）
