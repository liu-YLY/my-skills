# Testing Bundle Skill

> 测试能力 bundle 入口：统一路由到 5 个核心子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer / state-machine-test-engineer）+ 1 个协同 skill（change-impact-analyzer）。

## 简介

Testing Bundle 是一个元 skill（meta skill），本身不实现具体测试能力，而是作为测试能力的统一入口，根据用户意图自动路由到对应的子 skill。

### 为什么需要 Bundle

拆分后存在 6 个独立 skill：
- `test-strategy-engineer`：专注项目级测试策略
- `test-case-engineer`：专注功能用例生成
- `performance-test-engineer`：专注性能测试方案与瓶颈定位
- `bug-analyzer`：专注功能缺陷根因
- `state-machine-test-engineer`：专注状态机驱动的状态型需求测试（订单/审批/工单/会员等生命周期）
- `change-impact-analyzer`：专注代码变更影响分析（git diff × 用例交叉验证）

用户提出"测试相关"请求时，可能需要其中任何一个，也可能多个协同。Bundle 解决三个问题：
1. **统一入口**：用户无需预先判断该用哪个 skill
2. **混合意图协同**：自动编排多 skill 协同流程（7 条混合意图链）
3. **依赖关系管理**：显式声明 bug-analyzer 对 test-case-engineer 知识库的依赖、state-machine-test-engineer 对可选 state-machine MCP Server 的依赖、test-case-engineer 评审模式对可选 review-checker MCP Server 的依赖

## 子 skill 说明

| 子 skill | 职责 | 核心工作流 |
|---------|------|----------|
| [test-strategy-engineer](../test-strategy-engineer/) | 项目级测试策略 | 五阶段：项目特征 → 风险矩阵 → 分层 → 范围准入准出 →（可选）资源附录 |
| [test-case-engineer](../test-case-engineer/) | 功能用例生成 | 四阶段：理解需求 → 提取测试点 → 编写用例 → 自检补全 |
| [performance-test-engineer](../performance-test-engineer/) | 性能测试方案+瓶颈定位 | 四阶段：需求理解 → 场景设计 → 瓶颈定位 → 转交判断 |
| [bug-analyzer](../bug-analyzer/) | 功能缺陷根因 | 五步定位法：复现 → 隔离 → 定位 → 验证 → 报告 |
| [state-machine-test-engineer](../state-machine-test-engineer/) | 状态机建模+场景穷举 | 五阶段：状态型需求识别 → 状态机建模 → 完整性检查 → 10类场景穷举 →（可选）MCP 增强 |
| [change-impact-analyzer](../change-impact-analyzer/) | 代码变更影响分析 | 四阶段：收集输入 → Diff 解析 → 交叉分析 → 生成报告 |

## 路由规则

完整路由规则、7 条混合意图链、使用示例与反例黑名单见 [SKILL.md](SKILL.md)（唯一权威源，不在本 README 重复维护）。

## 安装方式

### 方式 1：整体安装（推荐）

```
skills/
├── testing-bundle/              ← 本 skill（路由入口）
├── test-strategy-engineer/      ← 子 skill（项目级策略）
├── test-case-engineer/          ← 子 skill（用例生成）
├── performance-test-engineer/   ← 子 skill（性能测试）
├── bug-analyzer/                ← 子 skill（Bug 分析）
├── state-machine-test-engineer/ ← 子 skill（状态机测试）
└── change-impact-analyzer/      ← 子 skill（变更影响分析，链 6 协同）
```

获得完整测试能力，bundle 自动路由，无需用户判断该用哪个子 skill。

### 方式 2：按需安装

- 只需项目级策略 → 仅安装 `test-strategy-engineer`
- 只需用例生成 → 仅安装 `test-case-engineer`
- 只需性能测试 → 仅安装 `performance-test-engineer`
- 只需 Bug 分析 → 仅安装 `bug-analyzer`（缺陷模式库引用会降级）
- 只需状态机测试 → 仅安装 `state-machine-test-engineer`（可选再装配套 MCP Server 进入增强模式）
- 只需变更影响分析 → 仅安装 `change-impact-analyzer`
- 不安装 `testing-bundle` 时，用户需自行判断该用哪个子 skill

## 知识库依赖

- `bug-analyzer` 依赖 `test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库），通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- `test-strategy-engineer` 与 `performance-test-engineer` 的知识库独立，不与其他子 skill 共享
- `state-machine-test-engineer` 知识库独立（含 4 个行业状态机模板：订单退款/审批流/会员/工单）；可选调用 `state-machine-testing-mcp` Server 做 Schema 校验与可视化，未安装时降级为纯 LLM 推理
- `test-case-engineer` 评审模式可选调用 `review-checker-mcp` Server 做 10 维度确定性校验（9 维度用例级校验 + 1 维度语义一致性冲突检测），未安装时降级为纯 LLM 推理

## 文件结构

```
testing-bundle/
├── SKILL.md                       # 入口（路由规则 + 协同流程）
├── README.md                      # 本说明文档
├── CHANGELOG.md                   # 版本变更记录
├── knowledge/
│   └── mixed-intent-chains.md     # 7 条混合意图链详细步骤流
└── test-prompts.json              # 路由验证 prompt
```

版本变更见 [CHANGELOG.md](CHANGELOG.md)。

---

**相关文档**：
- [SKILL.md](SKILL.md) - 完整路由规则与协同流程
- [CHANGELOG.md](CHANGELOG.md) - 版本变更记录
- [test-strategy-engineer](../test-strategy-engineer/) - 项目级测试策略子 skill
- [test-case-engineer](../test-case-engineer/) - 功能用例生成子 skill
- [performance-test-engineer](../performance-test-engineer/) - 性能测试子 skill
- [bug-analyzer](../bug-analyzer/) - 功能缺陷根因分析子 skill
- [state-machine-test-engineer](../state-machine-test-engineer/) - 状态机测试子 skill
- [change-impact-analyzer](../change-impact-analyzer/) - 变更影响分析子 skill（链 6 使用）
