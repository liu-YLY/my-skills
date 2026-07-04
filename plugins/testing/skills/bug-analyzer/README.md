# bug-analyzer Skill

> Bug 根因分析与缺陷定位技能包，v1.0.0。
> 由原 test-engineer v7.0.0 拆分而来，专注逆向根因分析。

## 核心能力

- **五步定位法**：复现 → 隔离 → 定位 → 验证 → 报告
- **根因分析框架**：鱼骨图（人/机/料/法/环）+ 5 Whys + 因果链追溯
- **防御性用例反推**：基于根因输出防御性测试点清单（完整用例生成转交 test-case-engineer）
- **结构化报告**：标准根因分析报告模板

## 与 test-case-engineer 的关系

| 维度 | bug-analyzer | test-case-engineer |
|------|--------------|-------------------|
| 方向 | 逆向（Bug → 根因） | 正向（需求 → 用例） |
| 输入 | Bug 现象/日志/复现步骤 | 需求文档/代码变更 |
| 输出 | 根因报告 + 防御性测试点清单 | 测试用例 |
| 协作 | 完成后转交 test-case-engineer 生成完整用例 | — |

## 文件结构

```
bug-analyzer/
├── SKILL.md                          # 入口 + 核心流程（五步定位法）
├── knowledge/
│   ├── root-cause-frameworks.md      # 鱼骨图/5 Whys/因果链/防御性用例反推
│   └── bug-patterns-index.md         # 指向 test-case-engineer 的共享缺陷模式库
├── integrations/
│   └── quickstart.md                 # 命令速查
├── scripts/
│   ├── convert_docs.py               # 文档转换（与 test-case-engineer 共用）
│   └── requirements.txt
└── test-prompts.json                 # 测试 prompt（3 个 Bug 分析场景）
```

## 快速开始

1. 用户描述 Bug 现象（必填）+ 环境/复现步骤（可选）
2. Skill 自动触发，进入步骤 1 复现
3. 按五步定位法执行，每步等待用户确认
4. 输出根因分析报告 + 防御性测试点清单

## 触发关键词

Bug分析、根因、缺陷定位、复现、5 Whys、鱼骨图、NullPointerException、500错误、测试环境与预发不一致
