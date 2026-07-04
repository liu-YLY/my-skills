# Testing Bundle Skill

> 测试能力 bundle 入口：统一路由到 test-case-engineer（正向用例生成）或 bug-analyzer（逆向根因分析）。

## 简介

Testing Bundle 是一个元 skill（meta skill），本身不实现具体测试能力，而是作为测试能力的统一入口，根据用户意图自动路由到对应的子 skill。

### 为什么需要 Bundle

拆分后存在两个独立 skill：
- `test-case-engineer`：专注正向用例生成（需求 → 测试用例）
- `bug-analyzer`：专注逆向根因分析（Bug → 修复建议）

用户提出"测试相关"请求时，可能需要其中任何一个，也可能两者都需要。Bundle 解决三个问题：
1. **统一入口**：用户无需预先判断该用哪个 skill
2. **混合意图协同**：自动编排"先分析后生成"的协同流程
3. **依赖关系管理**：显式声明 bug-analyzer 对 test-case-engineer 的知识库依赖

## 子 skill 说明

| 子 skill | 职责 | 核心工作流 |
|---------|------|----------|
| [test-case-engineer](../test-case-engineer/) | 正向用例生成 | 四阶段：理解需求 → 提取测试点 → 编写用例 → 自检补全 |
| [bug-analyzer](../bug-analyzer/) | 逆向根因分析 | 五步定位法：复现 → 隔离 → 定位 → 验证 → 报告 |

## 路由规则

Bundle 根据用户意图自动路由：

| 用户意图 | 路由到 |
|---------|--------|
| 生成/评审测试用例、需求分析、测试策略 | test-case-engineer |
| Bug 根因分析、缺陷定位、5 Whys、防御性用例反推 | bug-analyzer |
| 混合意图（如"分析 Bug 并补充用例"） | bug-analyzer → test-case-engineer |
| 意图不明确 | 追问用户 |

## 安装方式

### 方式 1：整体安装（推荐）

```
skills/
├── testing-bundle/         ← 本 skill（路由入口）
├── test-case-engineer/     ← 子 skill（用例生成）
└── bug-analyzer/           ← 子 skill（Bug 分析）
```

获得完整测试能力，bundle 自动路由，无需用户判断该用哪个子 skill。

### 方式 2：按需安装

- 只需用例生成 → 仅安装 `test-case-engineer`
- 只需 Bug 分析 → 仅安装 `bug-analyzer`（缺陷模式库引用会降级）
- 不安装 `testing-bundle` 时，用户需自行判断该用哪个子 skill

## 知识库依赖

`bug-analyzer` 的根因分析流程依赖 `test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库），通过相对路径引用：

```
bug-analyzer/knowledge/bug-patterns-index.md
  → 指向 ../test-case-engineer/knowledge/bug-patterns.md
```

**降级策略**：若 test-case-engineer 未安装，bug-analyzer 仍可工作，但"对照缺陷模式库"能力降级为通用模式兜底（输入校验/状态/权限/数据/UI 五类）。

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

### 示例 3：混合意图协同
```
用户：分析这个 Bug 并补充测试用例
→ bundle 路由到 bug-analyzer（输出防御性测试点清单）
→ 转交 test-case-engineer（基于清单生成完整用例）
→ 输出根因分析 + 完整用例
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

## 版本历史

- v1.0.0: 初始版本，作为 test-case-engineer + bug-analyzer 的 bundle 入口

---

**相关文档**：
- [SKILL.md](SKILL.md) - 完整路由规则与协同流程
- [test-case-engineer](../test-case-engineer/) - 正向用例生成子 skill
- [bug-analyzer](../bug-analyzer/) - 逆向根因分析子 skill
