# Testing Bundle Skill

> 测试能力 bundle 入口 v2.0.0：统一路由到 4 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer）。

## 简介

Testing Bundle 是一个元 skill（meta skill），本身不实现具体测试能力，而是作为测试能力的统一入口，根据用户意图自动路由到对应的子 skill。

### 为什么需要 Bundle

拆分后存在 4 个独立 skill：
- `test-strategy-engineer`：专注项目级测试策略
- `test-case-engineer`：专注功能用例生成
- `performance-test-engineer`：专注性能测试方案与瓶颈定位
- `bug-analyzer`：专注功能缺陷根因

用户提出"测试相关"请求时，可能需要其中任何一个，也可能多个协同。Bundle 解决三个问题：
1. **统一入口**：用户无需预先判断该用哪个 skill
2. **混合意图协同**：自动编排多 skill 协同流程
3. **依赖关系管理**：显式声明 bug-analyzer 对 test-case-engineer 知识库的依赖

## 子 skill 说明

| 子 skill | 职责 | 核心工作流 |
|---------|------|----------|
| [test-strategy-engineer](../test-strategy-engineer/) | 项目级测试策略 | 五阶段：项目特征 → 风险矩阵 → 分层 → 范围准入准出 →（可选）资源附录 |
| [test-case-engineer](../test-case-engineer/) | 功能用例生成 | 四阶段：理解需求 → 提取测试点 → 编写用例 → 自检补全 |
| [performance-test-engineer](../performance-test-engineer/) | 性能测试方案+瓶颈定位 | 四阶段：需求理解 → 场景设计 → 瓶颈定位 → 转交判断 |
| [bug-analyzer](../bug-analyzer/) | 功能缺陷根因 | 五步定位法：复现 → 隔离 → 定位 → 验证 → 报告 |

## 路由规则

Bundle 根据用户意图自动路由：

| 用户意图 | 路由到 |
|---------|--------|
| 测试策略、测试计划、测试分层、风险矩阵、准入准出 | test-strategy-engineer |
| 生成/评审测试用例、需求分析、单功能测试策略 | test-case-engineer |
| 性能测试、负载测试、TPS、响应时间、瓶颈 | performance-test-engineer |
| Bug 根因分析、缺陷定位、5 Whys、防御性用例反推 | bug-analyzer |
| 混合意图（4 条链） | 见 SKILL.md 混合意图链 |
| 意图不明确 | 追问用户 |

## 安装方式

### 方式 1：整体安装（推荐）

```
skills/
├── testing-bundle/              ← 本 skill（路由入口）
├── test-strategy-engineer/      ← 子 skill（项目级策略）
├── test-case-engineer/          ← 子 skill（用例生成）
├── performance-test-engineer/   ← 子 skill（性能测试）
└── bug-analyzer/                ← 子 skill（Bug 分析）
```

获得完整测试能力，bundle 自动路由，无需用户判断该用哪个子 skill。

### 方式 2：按需安装

- 只需项目级策略 → 仅安装 `test-strategy-engineer`
- 只需用例生成 → 仅安装 `test-case-engineer`
- 只需性能测试 → 仅安装 `performance-test-engineer`
- 只需 Bug 分析 → 仅安装 `bug-analyzer`（缺陷模式库引用会降级）
- 不安装 `testing-bundle` 时，用户需自行判断该用哪个子 skill

## 知识库依赖

- `bug-analyzer` 依赖 `test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库），通过相对路径 `../test-case-engineer/knowledge/bug-patterns.md` 引用
- `test-strategy-engineer` 与 `performance-test-engineer` 的知识库独立，不与其他子 skill 共享

## 使用示例

### 示例 1：自动路由到用例生成
```
用户：我有一个登录功能需要测试...
→ bundle 路由到 test-case-engineer
→ 输出测试用例
```

### 示例 2：自动路由到 Bug 分析
```
用户：线上重复扣款 Bug 帮我分析根因
→ bundle 路由到 bug-analyzer
→ 输出根因分析报告
```

### 示例 3：混合意图协同（Bug + 用例）
```
用户：分析这个 Bug 并补充测试用例
→ bundle 路由到 bug-analyzer（输出防御性测试点清单）
→ 转交 test-case-engineer（基于清单生成完整用例）
→ 输出根因分析 + 完整用例
```

### 示例 4：自动路由到测试策略
```
用户：新项目要制定测试策略，包含分层和准入准出
→ bundle 路由到 test-strategy-engineer
→ 输出项目级测试策略（分层 + 风险矩阵 + 准入准出）
```

### 示例 5：自动路由到性能测试
```
用户：支付接口要做性能测试，目标 TPS 2000
→ bundle 路由到 performance-test-engineer
→ 输出性能测试方案 + 场景设计 + 瓶颈定位流程
```

## 文件结构

```
testing-bundle/
├── SKILL.md           # 入口（路由规则 + 协同流程）
├── README.md          # 本说明文档
└── test-prompts.json  # 路由验证 prompt
```

## 反例与黑名单

- ❌ bundle 层重复实现子 skill 的能力
- ❌ 不判断意图直接调用某个子 skill
- ❌ 只装 bundle 不装子 skill（bundle 无法独立完成任何任务）
- ❌ 路由时不传递上下文
- ❌ 把性能问题路由到 bug-analyzer（应路由到 performance-test-engineer）
- ❌ 把项目级策略路由到 test-case-engineer（应路由到 test-strategy-engineer）

## 版本历史

- v1.0.0: 初始版本，2-skill 路由
- v2.0.0: 扩展为 4-skill 路由（+ test-strategy-engineer + performance-test-engineer），breaking change

---

**相关文档**：
- [SKILL.md](SKILL.md) - 完整路由规则与协同流程
- [test-strategy-engineer](../test-strategy-engineer/) - 项目级测试策略子 skill
- [test-case-engineer](../test-case-engineer/) - 功能用例生成子 skill
- [performance-test-engineer](../performance-test-engineer/) - 性能测试子 skill
- [bug-analyzer](../bug-analyzer/) - 功能缺陷根因分析子 skill
