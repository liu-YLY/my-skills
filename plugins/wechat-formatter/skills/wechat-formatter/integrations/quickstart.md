# 快速开始

> **何时阅读**：首次使用 wechat-formatter 排版文章时；安装环境时；排查常见问题时。
> **覆盖范围**：依赖安装、3 种典型用法、输出文件说明、故障排查、与五阶段流程的对应关系。
> **可跳过条件**：已熟悉环境配置且仅需查阅风格细节时跳过。

---

## 一、环境要求

### 1.1 Python 版本

- **Python 3.8 及以上**（推荐 3.10+）
- 检查命令：

```bash
python --version
```

输出应为 `Python 3.8.x` 或更高版本。低于 3.8 不支持，请先升级 Python。

### 1.2 依赖安装

阶段 5 生成可粘贴 HTML 依赖以下 Python 库：

```bash
pip install markdown beautifulsoup4
```

- `markdown`：Markdown → HTML 解析
- `beautifulsoup4`：HTML 节点遍历与内联样式注入

### 1.3 验证安装

```bash
python -c "import markdown, bs4; print('OK')"
```

输出 `OK` 表示依赖安装成功。

### 1.4 可选依赖

- 如果需要在本地预览 HTML，安装默认浏览器即可
- 如果需要使用 mdnice 等在线工具作为备选方案，无需本地依赖

---

## 二、3 种典型用法

### 用法 1：默认模式（自动分析 + 推荐 + 生成 HTML）

**适用场景**：不确定用什么风格，让 AI 自动分析内容并推荐。

**步骤**：

1. 把文章内容提供给 AI（粘贴文本或提供 .md 文件路径）
2. AI 执行阶段 1 分析内容，输出文章类型和核心特征
3. AI 执行阶段 2 推荐 2-3 种风格，等待用户选择（🔴 CHECKPOINT 1）
4. 用户输入编号选择风格
5. AI 执行阶段 3 按选定风格排版，输出格式化 Markdown
6. AI 执行阶段 4 校验（覆盖度 + 可读性 + 公众号兼容性）
7. AI 执行阶段 5 调用 `md2wechat.py` 生成 HTML 文件
8. 用户在浏览器打开 HTML，点击「复制到公众号」按钮，粘贴到微信编辑器

**示例对话**：

```
用户：请排版这篇文章：sample-input-testing-guide.md

AI：📊 内容分析结果：
   - 文章类型：技术教程
   - 核心特征：包含代码块、步骤、列表
   - 字数统计：约 800 字

   🎨 推荐风格（请选择）：
   1. tech-blog - 通用技术博客风，适合编程教程
   2. tutorial - 教程指南风，步骤清晰，适合操作类内容
   3. deep-dive - 深度干货风，适合原理剖析

   请输入编号选择，或输入其他风格代号：

用户：2

AI：（完成排版并生成 HTML 文件路径）
```

**对应五阶段**：完整执行阶段 1 → 2 → 3 → 4 → 5

---

### 用法 2：快速模式（指定风格代号，跳过分析）

**适用场景**：已经知道要用哪个风格，不需要 AI 推荐。

**步骤**：

1. 在对话中直接指定风格代号（如 `tech-blog`、`tutorial`、`deep-dive`、`casual-chat`、`apple`、`cyber`）
2. AI 跳过阶段 2，仅输出简版分析（要素统计 + 一句话定性）
3. AI 直接进入阶段 3 按指定风格排版
4. AI 执行阶段 4 简化校验（仅兼容性检查，跳过覆盖度和风格一致性）
5. AI 执行阶段 5 生成 HTML 文件

**示例对话**：

```
用户：用 tutorial 风格排版 sample-input-testing-guide.md

AI：（跳过推荐，直接完成排版 + HTML 生成）
```

**对应五阶段**：阶段 1（简版）→ 跳过阶段 2 → 阶段 3 → 阶段 4（简化）→ 阶段 5

**支持的风格代号**：

| 代号 | 风格名 | 适用场景 |
|------|--------|---------|
| `tech-blog` | 技术博客 | 编程教程、技术分享 |
| `tutorial` | 教程指南 | 操作指南、配置说明 |
| `deep-dive` | 深度干货 | 原理剖析、架构分析 |
| `casual-chat` | 轻松聊天 | 经验总结、技术随笔 |
| `apple` | 苹果风 | 产品设计、架构哲学 |
| `cyber` | 赛博朋克 | 安全技术、极客文化 |

---

### 用法 3：仅排版模式（不生成 HTML）

**适用场景**：只需要格式化 Markdown，自己用 mdnice 等工具应用 CSS。

**步骤**：

1. 在对话中明确说明不需要 HTML 输出
2. AI 执行阶段 1 → 2 → 3 → 4，输出格式化 Markdown 文件
3. 跳过阶段 5，不调用 `md2wechat.py`
4. 用户自行将 Markdown 粘贴到 mdnice 等工具，应用对应风格 CSS 后复制到公众号

**示例对话**：

```
用户：用 tech-blog 风格排版这篇文章，不需要生成 HTML

AI：（仅输出格式化 Markdown 文件路径）
```

**对应五阶段**：阶段 1 → 2 → 3 → 4 → 跳过阶段 5

**适合人群**：偏好手动控制 CSS 渲染、使用 mdnice / 135 编辑器 / 壹伴等第三方工具的作者。

---

## 三、输出文件说明

### 3.1 文件命名规则

| 输出类型 | 命名规则 | 示例 |
|---------|---------|------|
| 格式化 Markdown | `{原文件名}_formatted_{风格代号}.md` | `sample-input-testing-guide_formatted_tutorial.md` |
| 可粘贴 HTML | `{原文件名}_formatted_{风格代号}_wechat.html` | `sample-input-testing-guide_formatted_tutorial_wechat.html` |

### 3.2 输出路径

- **指定了输入文件路径**：输出到与输入文件相同的目录
- **未指定输入文件路径**（直接粘贴文本）：输出到当前工作目录根目录

### 3.3 文件头注释

每个输出 Markdown 文件头部包含 HTML 注释，记录排版元信息：

```html
<!--
排版风格：技术博客 (tech-blog)
排版时间：2026-05-22
原始文件：sample-input-testing-guide.md
图片占位：0 处
代码块：2 处
-->
```

### 3.4 HTML 文件特性

阶段 5 生成的 HTML 文件包含：

- 所有 CSS 样式以内联方式注入到对应 HTML 标签（适配微信公众号编辑器）
- 顶部有「复制到公众号」按钮，点击后自动复制全文到剪贴板
- 在浏览器中打开后即可使用，无需额外配置

---

## 四、与 SKILL.md 五阶段流程的对应关系

| 阶段 | 用法 1（默认） | 用法 2（快速） | 用法 3（仅排版） |
|------|--------------|--------------|----------------|
| 阶段 1 分析内容 | ✅ 完整分析 | ✅ 简版分析 | ✅ 完整分析 |
| 🔴 阶段 2 匹配风格 | ✅ 推荐 2-3 种 | ❌ 跳过 | ✅ 推荐 2-3 种 |
| 阶段 3 执行排版 | ✅ 按选定风格 | ✅ 按指定风格 | ✅ 按选定风格 |
| 🔴 阶段 4 输出校验 | ✅ 完整校验 | ✅ 简化校验 | ✅ 完整校验 |
| 阶段 5 生成 HTML | ✅ 生成 | ✅ 生成 | ❌ 跳过 |

> 🔴 标记的为 CHECKPOINT 阶段，需要用户确认后才能继续。

---

## 五、故障排查

### 5.1 依赖缺失

**现象**：阶段 5 执行 `md2wechat.py` 时报错 `ModuleNotFoundError: No module named 'markdown'` 或 `No module named 'bs4'`。

**原因**：未安装 Python 依赖。

**解决**：

```bash
pip install markdown beautifulsoup4
```

如果使用虚拟环境，确保在正确的环境中安装：

```bash
# 激活虚拟环境后
pip install markdown beautifulsoup4
```

**验证**：

```bash
python -c "import markdown, bs4; print('OK')"
```

---

### 5.2 CSS 提取失败

**现象**：阶段 5 生成的 HTML 文件无样式（白底黑字），或控制台输出 `警告: 在 styles/xxx.md 中未找到 CSS 代码块`。

**原因**：`styles/{style}.md` 文件中的 CSS 代码块标记缺失或格式错误。

**解决**：

1. 打开 `styles/{style}.md` 文件
2. 确认 CSS 代码被包裹在 ` ```css ` 和 ` ``` ` 之间（反引号三个，标记为 css）
3. 确认 CSS 代码块前后没有多余缩进或字符
4. 如果文件损坏，重新安装 skill 或从备份恢复

**示例（正确格式）**：

````markdown
# 技术博客 CSS

```css
#nice {
    font-family: ...;
}
```
````

---

### 5.3 模块语法错误

**现象**：阶段 4 校验时报错 `未知模块名`、`缺少必填字段` 或 `模块嵌套`。

**原因**：文章中使用了 `:::module` 语法但格式不正确。

**解决**：

1. **未知模块名**：检查模块名是否在 9 大类清单内（参考 [knowledge/module-design.md](../knowledge/module-design.md) 第二节）
2. **缺少必填字段**：对照 [layout/layout-modules.md](../layout/layout-modules.md) 中各模块的字段表，补齐必填字段
3. **模块嵌套**：把嵌套的模块拆成并列的两个模块（参考 [knowledge/module-design.md](../knowledge/module-design.md) 第 3.3 节）
4. **结束标记缺失**：每个模块必须以单独一行的 `:::` 结尾，前后不能有其他内容

**自检命令**：

阶段 4 会自动调用校验，输出详细错误清单。按清单逐条修正即可。

---

## 六、下一步

完成快速开始后，建议继续了解：

- **风格详情**：[templates/template-index.md](../templates/template-index.md) 查看全部 6 种风格的选择指南
- **高级模块**：[knowledge/module-design.md](../knowledge/module-design.md) 学习 `:::module` 语法和组合规则
- **品牌配置**：[knowledge/brand-profile-spec.md](../knowledge/brand-profile-spec.md) 配置长期品牌风格
- **常见陷阱**：[knowledge/wechat-traps.md](../knowledge/wechat-traps.md) 避免公众号排版常见错误
- **示例参考**：[examples/](../examples/) 目录有 6 种风格的完整输出示例

---

> **参考**：完整工作流定义见 [SKILL.md](../SKILL.md)，转换脚本细节见 [scripts/md2wechat.py](../scripts/md2wechat.py)。
