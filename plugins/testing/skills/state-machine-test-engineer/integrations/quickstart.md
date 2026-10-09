# MCP Server 配置快速上手

> 本文档说明如何配置 `state-machine-testing-mcp` Server，让 state-machine-test-engineer skill 进入增强模式。

> ✅ **当前 MCP Server 状态（v0.4.6）**：MCP 协议层（stdio + streamable-http 传输）和真实工具调用已通过端到端测试。按本文档完成配置后，**增强模式可用**。`build_state_machine` 为确定性实现（行业模板加载，不内置 LLM）。未安装或调用失败时 skill 自动降级为独立模式。

## 三种运行模式回顾

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **增强模式** | MCP 工具已暴露且参数 Schema 兼容 | skill 自身推理 + MCP 做校验/穷举/可视化复核 |
| **独立模式** | MCP 未安装 | skill 纯 LLM 推理执行全流程 |
| **降级模式** | MCP 调用失败 | 自动回退到独立模式 |

**关键原则**：skill 始终是主，MCP 是复核器。未配置 MCP 时 skill 完全可用，配置后获得额外能力。

## 增强模式额外能力

| 能力 | 独立模式 | 增强模式 |
|---|---|---|
| 状态机建模 | ✓（LLM 推理） | ✓（LLM 推理） |
| 完整性检查 | ✓（skill 内置 9 项自检） | ✓（MCP validate_state_machine 双重校验） |
| 10 类场景穷举 | ✓（skill 自行穷举） | ✓（skill 穷举 + MCP generate_scenarios 交叉复核） |
| Mermaid 状态图 | ✓（skill 手写，样式略差） | ✓（MCP 生成，标准格式） |
| 覆盖度报告 | 简单统计 | MCP 详细报告（转换/禁止/类型/依据分布） |
| 输出格式 | YAML/JSON | YAML/JSON + Markdown + Mermaid |

## 前置条件

- Python 3.11+
- pip 或 uv 包管理器
- 操作系统：Linux / macOS / Windows

## 安装步骤

### 步骤 1：克隆/定位 MCP Server 目录

MCP Server 与 skill 同仓，位于：

```
plugins/testing/mcp-servers/state-machine-testing/
```

源码 URL 用于定位仓库，不证明本次修复已在远程发布。使用与当前 Skill 契约匹配的源码 checkout 或发行版本，先核对已安装服务版本与 `tools/list` 参数 Schema；旧服务不支持新可选字段时省略这些字段并保留人工说明，降级能力单列，不声称新能力增强已可用。

复制安装 Skill 不包含 MCP Server；未安装或未注册工具时使用独立模式，不能把 Skill 安装成功当作 MCP 增强可用。另行克隆/定位源码仓库后，参考 [MCP Server README](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/mcp-servers/state-machine-testing/README.md) 完成开发。安装与开发细节见该 README。

### 步骤 2：安装 Python 依赖

```bash
cd plugins/testing/mcp-servers/state-machine-testing/
pip install -e .
# 或使用 uv
uv pip install -e .
```

依赖清单（pyproject.toml）：
- `mcp >= 0.9.0, < 2.0.0`（2.0.0 移除了 `mcp.server.fastmcp` 模块）
- `pydantic >= 2.0`
- `pyyaml >= 6.0`（解析行业模板）
- Python 3.11+

### 步骤 3：验证 Server 可独立启动

```bash
python -m state_machine_testing_mcp.server --help
```

应输出 5 个工具的帮助信息。

### 步骤 4：配置 Trae MCP 客户端

> **配置文件职责区分**：
> - `~/.trae/mcp_servers.json`（步骤 4）：让 Trae 启动并注册 MCP Server，skill 通过 Trae 通道调用 MCP 工具。
> - `~/.trae/state-machine-mcp.json`（步骤 5）：控制 skill 自身的 MCP 探测开关（`enabled`）、fallback 策略、日志级别。
> - 环境变量 `STATE_MACHINE_MCP_ENABLED`（方式 B）：轻量启用信号，skill 探测时优先检查。
>
宿主工具清单是跨宿主能力依据。Trae 文件和环境变量仅是 Trae 的配置示例，均非其他宿主前置；用户显式禁用优先。已有工具即可增强，不要求三者同时存在。详见 [state-machine-core.md §5.1](../state-machine-core.md)。

#### 方式 A：通过 Trae 配置文件（推荐）

编辑 `~/.trae/mcp_servers.json`（若不存在则创建），加入：

```json
{
  "mcpServers": {
    "state-machine-testing": {
      "command": "python",
      "args": [
        "-m", "state_machine_testing_mcp.server"
      ],
      "cwd": "/absolute/path/to/plugins/testing/mcp-servers/state-machine-testing/",
      "env": {
        "PYTHONPATH": "/absolute/path/to/plugins/testing/mcp-servers/state-machine-testing/src/"
      },
      "disabled": false,
      "autoApprove": [
        "build_state_machine",
        "validate_state_machine",
        "generate_scenarios",
        "export_artifacts",
        "check_coverage"
      ]
    }
  }
}
```

注意把 `cwd` 和 `PYTHONPATH` 中的 `/absolute/path/to/` 替换为你的实际路径。

#### 方式 B：通过环境变量（轻量启用）

环境变量仅表示显式偏好；未设置不阻止使用已暴露工具，设置为 false 表示禁用。实际服务注册沿用当前宿主配置，环境变量不创建 MCP 通道。

在 shell 配置文件（`~/.bashrc` / `~/.zshrc`）中加入：

```bash
export STATE_MACHINE_MCP_ENABLED=true
```

skill 优先检查当前宿主工具；无工具时进入独立模式。其他宿主使用其自身的 MCP 注册方式。

### 步骤 5：配置 skill 可选参数（可选）

编辑 `~/.trae/state-machine-mcp.json`（若不存在则创建）：

```json
{
  "enabled": true,
  "transport": "stdio",
  "command": "python",
  "args": ["-m", "state_machine_testing_mcp.server"],
  "fallback_on_error": true,
  "log_level": "warn"
}
```

字段说明：

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `enabled` | bool | false | 显式启用 MCP 增强 |
| `transport` | "stdio" \| "http" | "stdio" | 传输方式，本地用 stdio |
| `command` | string | — | 启动 Server 的命令 |
| `args` | string[] | — | 命令参数 |
| `fallback_on_error` | bool | true | MCP 失败时是否降级到独立模式 |
| `log_level` | "debug" \| "info" \| "warn" \| "error" | "warn" | 日志级别 |

### 步骤 6：验证配置

先查看当前宿主 tools/list；需要真实健康调用时使用 core §5.1 的合法模型。JSON Schema 参数错误先修正输入，不能当连接失败。业务校验 pass/warn/fail 均是有效响应。工具列表探测最多等待 3s；只读调用 10s 超时可重试一次，之后降级。

在 Trae 中调用 state-machine-test-engineer skill，输入测试需求：

```
用户：测试订单退款流程，订单状态包括待支付/已支付/已取消/退款中/退款成功/退款失败
```

若配置成功，输出首行应标注：

```
✓ MCP 增强模式
```

并包含 Mermaid 状态图与覆盖度报告。

若配置失败，输出首行会标注：

```
⚠ 独立模式（未校验）
```

或

```
⚠ 降级模式（MCP 失败：原因）
```

此时 skill 仍完整可用，只是失去 MCP 增强能力。

## 故障排查

### 问题 1：MCP Server 启动失败

```bash
# 检查 Python 版本
python --version  # 应 >= 3.11

# 检查依赖
pip list | grep -E "mcp|pydantic"

# 手动启动测试
python -m state_machine_testing_mcp.server
```

### 问题 2：Trae 未识别到 MCP Server

- 确认 `~/.trae/mcp_servers.json` 格式正确（JSON 校验）
- 确认 `cwd` 和 `PYTHONPATH` 为绝对路径
- 重启 Trae

### 问题 3：skill 仍显示"独立模式"

- 检查用户是否显式禁用 MCP，再查看宿主工具清单
- 工具不存在、连接失败、超时和参数错误分别报告；缺少 Trae 文件不证明服务不可用
- 若返回业务 warn/fail，服务已响应，按业务结果处理，不判离线

### 问题 4：MCP 调用超时

skill 默认超时 10s，单次重试。若仍超时：
- 检查 Server 启动是否缓慢（首次 import 依赖耗时）
- 在 `~/.trae/state-machine-mcp.json` 中确认 `fallback_on_error: true`，让 skill 自动降级

## 卸载

### 移除 MCP 增强

1. 编辑 `~/.trae/mcp_servers.json`，删除 `state-machine-testing` 条目
2. 或设置 `~/.trae/state-machine-mcp.json` 的 `enabled: false`
3. skill 自动回退到独立模式，无需重新安装

### 完全卸载

```bash
cd plugins/testing/mcp-servers/state-machine-testing/
pip uninstall state-machine-testing-mcp
```

## 5 个 MCP 工具说明

| 工具名 | 用途 | 何时被 skill 调用 |
|---|---|---|
| `build_state_machine` | 确定性加载行业模板（order-refund/approval-flow/membership/ticket）作为建模起点；自由文本建模由 skill 自身完成 | skill 阶段 2（可选，模板起步） |
| `validate_state_machine` | 校验状态机完整性与一致性 | skill 阶段 3（完整性检查） |
| `generate_scenarios` | 基于状态机穷举 10 类场景 | skill 阶段 4（交叉复核） |
| `export_artifacts` | 导出 Markdown / JSON / Mermaid | skill 阶段 5（导出） |
| `check_coverage` | 覆盖度检查 | skill 阶段 5（覆盖度报告） |

工具详细签名见 [MCP Server README](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/mcp-servers/state-machine-testing/README.md#工具集)。

## 隐私与安全

- MCP Server 本地运行，不外发数据
- 全部 5 个工具均为确定性计算（v0.4.6 起 `build_state_machine` 为行业模板加载，不内置 LLM），不发任何数据出本机
- HTTP 传输模式（`--transport http`）默认仅监听 127.0.0.1，仅本机可访问

---

**相关文档**：
- [state-machine-test-engineer SKILL.md](../SKILL.md) - skill 完整方法论
- [MCP Server README](https://github.com/liu-YLY/my-skills/blob/main/plugins/testing/mcp-servers/state-machine-testing/README.md) - Server 安装与开发
- [设计文档](https://github.com/liu-YLY/my-skills/blob/main/docs/superpowers/specs/2026-07-18-state-machine-testing-design.md) - 完整设计 spec
