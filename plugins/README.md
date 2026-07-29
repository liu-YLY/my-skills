# Plugins

> 本目录是 my-skill 项目的 plugin 集合根目录，采用「单 repo + marketplace 多 plugin」结构（参考 [obra/superpowers](https://github.com/obra/superpowers) 与 [anthropics/claude-code](https://github.com/anthropics/claude-code)）。
>
> 每个 plugin 子目录是一个独立的可发布单元，包含自身的多 runtime 适配（`.claude-plugin/` + `.cursor-plugin/` + `.codex-plugin/`）、skills 子目录与说明文档。

## Plugin 清单

| Plugin | 版本 | 类别 | 简介 | 包含 skill 数 |
|---|---|---|---|---|
| [testing](./testing/) | v3.0.0 | testing | 测试能力 bundle：策略 / 用例 / 性能 / Bug 根因 / 状态机测试 | 6（1 bundle + 5 子 skill）+ 1 独立 skill + 1 可选 MCP Server |
| [wechat-formatter](./wechat-formatter/) | v2.0.0 | content | 微信公众号排版：6 种风格 + 高级排版模块 + HTML 生成 | 1 |

## 安装方式

详细安装步骤见根目录 [README.md](../README.md#安装与配置) 的「安装与配置」章节。三种方式概览：

| 方式 | 适用 | 命令示例 |
|---|---|---|
| `npx skills add` | 跨 runtime（推荐） | `npx skills add liu-YLY/my-skills --skill 'testing-bundle' -g -y` |
| Plugin Marketplace | Claude Code 原生 | `/plugin install testing-bundle@my-skill-marketplace` |
| 本地脚本 | 离线 / 兜底 | `.\scripts\install-testing-bundle.ps1` |

## 目录约定

每个 plugin 子目录应满足以下结构：

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Claude Code plugin manifest（必备）
├── .cursor-plugin/
│   └── plugin.json          # Cursor plugin manifest（可选）
├── .codex-plugin/
│   └── plugin.json          # Codex plugin manifest（可选）
├── skills/                  # runtime 扫描此目录加载 skill（必备）
│   └── <skill-name>/
│       ├── SKILL.md         # skill 入口
│       ├── README.md        # skill 说明
│       ├── test-prompts.json
│       ├── knowledge/       # 知识库（可选）
│       ├── integrations/    # 集成文档（可选）
│       └── ...
├── mcp-servers/             # 可选配套 MCP Server
├── scripts/                 # plugin 级脚本（可选）
└── README.md                # plugin 说明文档（必备）
```

## marketplace 注册

顶层 `.claude-plugin/marketplace.json` 注册所有 plugin 的发布入口：

```json
{
  "name": "my-skill-marketplace",
  "plugins": [
    { "name": "testing-bundle",    "source": "./plugins/testing/",         "category": "testing" },
    { "name": "wechat-formatter",  "source": "./plugins/wechat-formatter/", "category": "content" }
  ]
}
```

新增 plugin 时需同步更新 marketplace.json。
