# 安装指南

> 从 README.md 拆分，包含环境要求、3 种安装方式、安装后配置、故障排查。技能详细介绍见 [skills-overview.md](skills-overview.md)。

## 安装与配置

### 环境要求

| 环境 | 要求 | 说明 |
|------|------|------|
| **操作系统** | Windows / macOS / Linux | 跨平台支持 |
| **运行环境** | Claude Code / Cursor / Codex / OpenCode 等 | 支持 AI 技能的 IDE |
| **Node.js** | v18+（推荐） | 用于 skills CLI，可选 |
| **Python** | 3.8+（可选） | 用于工具脚本，可选 |

### 安装方式对比

本项目提供三种安装方式：

| 方式 | 推荐度 | 适用场景 | 优势 | 操作难度 |
|------|--------|----------|------|----------|
| **方式 1：npx skills add** | ⭐⭐⭐⭐⭐ | 跨平台、跨 runtime | 自动适配 70+ runtime，按 skill 粒度选择 | 中等 |
| **方式 2：Plugin Marketplace** | ⭐⭐⭐⭐ | Claude Code 用户 | 原生支持，一键安装整个 plugin | 简单 |
| **方式 3：本地脚本** | ⭐⭐⭐ | 离线安装、无 Node.js | 无需网络，灵活控制安装路径 | 较复杂 |

### 重要提示

> **bug-analyzer 依赖说明**：bug-analyzer 的 SKILL.md 引用 `../test-case-engineer/knowledge/bug-patterns.md`（缺陷模式库）。单独安装时该相对路径会失效，根因分析步骤 2/3 的"对照缺陷模式库"能力会降级（仍有通用模式兜底）。**建议与 test-case-engineer 一起安装**。

> **review-checker MCP Server 依赖说明**：review-checker 是 test-case-engineer 评审模式的可选增强组件（位于 plugins/testing/mcp-servers/review-checker/），未安装时评审模式降级为纯 LLM 推理。安装方式见 [review-checker README](../plugins/testing/mcp-servers/review-checker/README.md)。

---

### 方式 1：npx skills add（推荐）

使用 [skills CLI](https://skills.sh)（Agent 界的 npm）安装，自动适配 Claude Code / Cursor / Codex / OpenCode 等 70+ runtime。

#### 前置条件

安装 Node.js v18+

#### 查看可用 skill

```bash
# 列出仓库所有可安装的 skill
npx skills add liu-YLY/my-skills --list
```

#### 安装命令

**场景 1：安装所有 skill（推荐）**
```bash
# 包含 testing-bundle + 4 个子 skill + wechat-formatter
npx skills add liu-YLY/my-skills --skill '*' -g -y
```

**场景 2：仅安装测试能力 bundle**
```bash
# 安装 6 个 skill：testing-bundle + test-strategy-engineer + test-case-engineer + performance-test-engineer + bug-analyzer + state-machine-test-engineer
npx skills add liu-YLY/my-skills \
  --skill 'testing-bundle' \
  --skill 'test-strategy-engineer' \
  --skill 'test-case-engineer' \
  --skill 'performance-test-engineer' \
  --skill 'bug-analyzer' \
  -g -y
```

**场景 3：仅安装微信公众号排版**
```bash
npx skills add liu-YLY/my-skills --skill 'wechat-formatter' -g -y
```

**场景 4：指定安装到特定 runtime**
```bash
# 安装到 Claude Code 和 Cursor
npx skills add liu-YLY/my-skills --skill 'testing-bundle' -a claude-code -a cursor -g -y
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `-g, --global` | 全局安装（`~/<agent>/skills/`），不加则装到项目级（`./<agent>/skills/`） |
| `-a, --agent <agents...>` | 指定目标 runtime（claude-code / cursor / codex / opencode 等） |
| `-s, --skill <skills...>` | 按 skill 名选择，支持通配符（如 `test-*`），`'*'` 表示全部 |
| `-y, --yes` | 跳过确认提示（CI/CD 友好） |
| `--copy` | 复制文件而非 symlink（默认 symlink，便于更新） |

---

### 方式 2：Plugin Marketplace（Claude Code 原生）

Claude Code 用户可通过原生 `/plugin` 命令，按 plugin 粒度一键安装。

#### 安装步骤

```
# 步骤 1：注册 marketplace（只需执行一次）
/plugin marketplace add liu-YLY/my-skills

# 步骤 2：安装测试能力 bundle
# 含 testing-bundle + 4 个子 skill（test-strategy-engineer / test-case-engineer / performance-test-engineer / bug-analyzer）
/plugin install testing-bundle@my-skill-marketplace

# 步骤 3：安装微信公众号排版 skill（可选）
/plugin install wechat-formatter@my-skill-marketplace
```

> **说明**：本项目采用「单 repo + marketplace 多 plugin」结构（参考 [obra/superpowers](https://github.com/obra/superpowers)）。Cursor/Codex 用户可指向 plugin source 子目录安装，详见各 runtime 的 plugin 文档。

---

### 方式 3：本地脚本（兜底方案）

适用于未安装 Node.js 或需要离线安装的场景。

#### Windows（PowerShell）

```powershell
# 默认安装（装到 ~\.claude\skills）
.\scripts\install-testing-bundle.ps1

# 指定安装目录
.\scripts\install-testing-bundle.ps1 -TargetDir "C:\Users\<用户名>\.cursor\skills"

# 卸载
.\scripts\install-testing-bundle.ps1 -Uninstall
```

#### macOS / Linux

```bash
# 手动复制技能目录到目标 runtime 的 skills 目录
# Claude Code: ~/.claude/skills/
# Cursor: ~/.cursor/skills/
# Codex: ~/.codex/skills/

# 示例：复制 testing-bundle 到 Claude Code
cp -r plugins/testing/skills/testing-bundle ~/.claude/skills/
cp -r plugins/testing/skills/test-strategy-engineer ~/.claude/skills/
cp -r plugins/testing/skills/test-case-engineer ~/.claude/skills/
cp -r plugins/testing/skills/performance-test-engineer ~/.claude/skills/
cp -r plugins/testing/skills/bug-analyzer ~/.claude/skills/

# 示例：复制 wechat-formatter
cp -r plugins/wechat-formatter/skills/wechat-formatter ~/.claude/skills/
```

---

### 安装后配置

安装完成后，请按顺序执行以下操作：

#### 步骤 1：安装工具脚本依赖（可选）

如果需要使用 testing plugin 内的 Python 脚本（如 convert_docs.py 文档转换降级方案）：

```bash
cd plugins/testing/scripts
pip install -r requirements.txt
```

#### 步骤 2：重启运行环境

重启你的 runtime（Claude Code / Cursor / Codex 等），让其重新扫描 skills 目录，技能会自动识别并注册。

#### 步骤 3：验证安装

在 runtime 中测试技能是否正常工作：

**验证方式 1：直接输入技能名称**
```
测试用例工程师
```

**验证方式 2：描述需求触发技能**
```
我有一个用户登录功能需要测试...
```

如果技能正常激活，会看到技能名称和版本信息。

---

### 故障排查

#### 问题 1：skill 未被识别

**原因**：runtime 未重新扫描 skills 目录  
**解决**：完全重启 runtime（不是新建终端窗口）

#### 问题 2：bug-analyzer 功能降级

**原因**：单独安装 bug-analyzer，缺少 bug-patterns.md  
**解决**：同时安装 test-case-engineer（包含缺陷模式库）

#### 问题 3：npx skills add 命令失败

**原因**：Node.js 版本过低或未安装  
**解决**：
1. 安装 Node.js v18+
2. 或使用方式 3（本地脚本）安装

#### 问题 4：PowerShell 脚本执行权限错误

**原因**：Windows 默认禁止运行未签名脚本  
**解决**：
```powershell
# 临时允许运行脚本
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 然后执行安装脚本
.\scripts\install-testing-bundle.ps1
```
