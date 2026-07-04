# 缺陷模式库索引（共享引用）

> **何时阅读**：根因分析阶段需要查阅缺陷模式时加载本索引，再决定是否加载完整缺陷模式库。

## 共享来源

完整的缺陷模式库位于：

```
../test-case-engineer/knowledge/bug-patterns.md
```

该文件由 test-case-engineer skill 主维护，bug-analyzer skill 通过相对路径引用，避免内容重复与分叉。

## 使用场景

bug-analyzer 在以下场景查阅缺陷模式库：

1. **复现阶段**：对照缺陷模式判断 Bug 现象属于哪类常见模式
2. **定位阶段**：将症状与「缺陷模式 → 测试点映射」表对照，缩小根因范围
3. **报告阶段**：在根因分析报告中引用相关缺陷模式，提供修复建议的依据
4. **防御性用例反推**：基于缺陷模式生成防御性测试点清单

## 加载方式

```markdown
# 直接引用
参考 ../test-case-engineer/knowledge/bug-patterns.md 中的「{章节名}」

# 示例
参考 ../test-case-engineer/knowledge/bug-patterns.md 中的「状态与流程类」
参考 ../test-case-engineer/knowledge/bug-patterns.md 中的「领域特定缺陷模式 - 支付/金额」
```

## 内容速览（详细内容见共享文件）

缺陷模式库包含以下章节：

- 通用缺陷模式（5 类）：输入校验 / 状态与流程 / 权限与安全 / 数据与接口 / UI 与交互
- 领域特定核心模式：支付/金额 / 搜索/筛选 / 通知/消息 / 文件上传
- 安全专项检查清单（10 项）
- 「功能特征 → 缺陷模式」自动映射表
