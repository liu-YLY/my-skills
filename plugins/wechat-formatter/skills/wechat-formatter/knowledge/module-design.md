# 高级排版模块设计原则

> **何时阅读**：阶段 3 排版时使用高级模块；新增/扩展模块时；阶段 4 校验模块语法时。
> **覆盖范围**：9 大类模块清单、`:::module` 语法规范、模块组合规则、设计原则、与 CSS 的对应关系。
> **可跳过条件**：仅使用基础 Markdown 排版时跳过；模块使用细则请配合 [layout/layout-modules.md](../layout/layout-modules.md) 阅读。

---

## 一、设计目标

高级排版模块是 wechat-formatter v3.0.0 引入的核心能力，目标是把「视觉卡片」从 Markdown 流式文本里独立出来，让作者用 `:::module` 语法声明结构化组件，由 `scripts/md2wechat.py` 转换为带内联样式的微信公众号 HTML。

模块设计的三大目标：

1. **降低阅读决策成本**：先告诉读者「值不值得读」「记住什么」「下一步做什么」
2. **品牌一致性**：通过 hero / verdict / cta 等模块固化品牌识别度
3. **可组合可校验**：模块之间有明确的组合规则，便于阶段 4 自动校验

---

## 二、9 大类模块清单

依据「4 件事原则」（attention / readability / memorability / conversion），9 大类模块归类如下：

| 类别 | 模块 | 用途 | 4 件事归属 |
|------|------|------|----------|
| **1. opening 开场类** | `hero`, `toc`, `cards`, `part`, `label-title` | 文章开篇第一屏 | attention / readability |
| **2. infographic 信息图类** | `metrics`, `compare`, `steps`, `timeline`, `infographic` | 数据可视化展示 | readability |
| **3. judgment 判断类** | `verdict`, `audience-fit`, `myth-fact`, `manifesto`, `bridge` | 核心立场表达 | memorability |
| **4. evidence 证据类** | `quote`, `image-annotate`, `image-compare`, `image-steps`, `image-text` | 支撑判断的证据 | readability |
| **5. conversion 行动类** | `cta`, `faq`, `checklist`, `cases` | 促进读者行动 | conversion |
| **6. brand 品牌类** | `author-card`, `brand-banner` | 建立品牌识别度 | memorability |
| **7. callout 提示类** | `callout`, `highlight` | 强调重要信息 | attention |
| **8. free-layout 自由布局类** | `split`, `columns` | 灵活布局选项 | readability |
| **9. interactive 交互类** | `question`, `poll` | 增加读者参与度 | conversion |

> 各模块的字段定义和示例见 [layout/layout-modules.md](../layout/layout-modules.md)。

---

## 三、`:::module` 语法规范

### 3.1 基本结构

每个模块由三部分组成：开始标记、正文内容、结束标记。

```markdown
:::模块名
字段名: 字段值
:::
```

- **开始标记**：`:::` 紧跟模块名，不能有空格（如 `:::hero` 合法，`::: hero` 非法）
- **结束标记**：单独一行的 `:::`，前后不能有其他内容
- **正文内容**：位于开始标记与结束标记之间，支持字段、行、参数三种格式

### 3.2 三种正文格式

#### (1) 字段格式（fields）

每行 `key: value`，适用于结构化卡片。

```markdown
:::hero
eyebrow: 深度观察
title: 高级排版服务阅读决策
subtitle: 主题决定气质，模块决定读者能不能看懂
:::
```

#### (2) 行格式（rows），可带标题

每行一条，列用 `|` 分隔，模块名后可加 `[卡片标题]`。

```markdown
:::steps[落地步骤]
01 | 发现模块 | layout list 列出所有可用模块
02 | 查看规格 | layout show 确认字段和示例
:::
```

#### (3) 参数格式

模块名后用 `{参数名=参数值}` 指定参数，多个参数用空格分隔。

```markdown
:::columns{columns=2 gap=16}
第一列内容
---
第二列内容
:::
```

### 3.3 嵌套规则

**严禁模块嵌套**。一个模块的结束标记 `:::` 必须出现在下一个模块开始标记之前。如果需要在模块内放图片或代码，使用对应的图片字段（如 `image-steps` 的 `step`/`desc`/Markdown 图片组合）。

**非法示例**：

```markdown
:::hero
title: 标题
:::callout
tip | 这是嵌套的提示
:::
:::
```

**合法替代**：把嵌套内容拆成两个并列模块。

### 3.4 字段约定

- 必填字段缺失时，转换脚本输出警告但保留原文，由阶段 4 校验拦截
- 字段值不强制引号，包含特殊字符（如 `:` `|`）时建议用反引号或单独成段
- 重复字段（如 `point: 01 | ...`、`step: ...`）按出现顺序渲染

---

## 四、模块组合规则与限制

### 4.1 互斥规则（一篇文章只能出现一次）

下列模块在单篇文章中**最多出现一次**：

| 模块 | 原因 |
|------|------|
| `hero` | 第一屏只能有一个主视觉，多个会让读者迷失 |
| `verdict` | 核心判断必须唯一，否则品牌记忆点散失 |
| `manifesto` | 宣言卡天然是单点声明 |
| `cta` | 行动召唤必须收敛到一个明确的下一步 |
| `brand-banner` | 品牌横幅全局唯一 |

### 4.2 可重复模块

下列模块可多次出现，但需控制数量：

| 模块 | 建议次数 | 累计上限 |
|------|---------|---------|
| `callout` | 2-4 次 | 6 次 |
| `quote` | 1-3 次 | 4 次 |
| `part` | 每大章节 1 次 | 视章节数 |
| `steps` | 1-2 次 | 3 次 |
| `metrics` / `compare` | 1-2 次 | 3 次 |

### 4.3 推荐组合（按文章类型）

| 文章类型 | 推荐组合 | 总模块数 |
|---------|---------|---------|
| 观点文 | `hero` + `verdict` + `cta` | 3 |
| 数据报告 | `hero` + `metrics` + `compare` + `cta` | 4 |
| 教程 | `hero` + `steps` + `callout` + `faq` | 4 |
| 产品发布 | `hero` + `cards` + `cases` + `cta` | 4 |
| 经验复盘 | `hero` + `timeline` + `quote` + `verdict` | 4 |
| 品牌长文 | `hero` + `manifesto` + `part` × N + `author-card` | 5-7 |

### 4.4 互斥组合

- `hero` 与 `label-title` 二选一（都是开场类，避免重复铺垫）
- `toc` 与 `cards` 二选一（目录类组件，不要同时使用）
- `manifesto` 与 `verdict` 不同时出现（都属于判断类，避免立场分散）
- `split` 与 `columns` 不连续使用（自由布局组件连续会让排版失去节奏）

### 4.5 模块数量上限

- 单篇文章模块总数 **不超过 7 个**
- 视觉重量相近的模块不要连续出现（如 `metrics` 后不要立刻接 `compare`）
- 模块与正文段落穿插，避免连续 3 个模块之间没有过渡文字

---

## 五、模块设计原则

### 5.1 单一职责

每个模块只服务 4 件事中的一件。新增模块时必须明确归属哪件事，否则不予收录。

- ❌ 反例：一个模块既展示数据又号召行动
- ✅ 正例：`metrics` 只负责数据展示，`cta` 只负责行动召唤

### 5.2 可读性优先

模块是阅读体验的工具，不是装饰品。设计时遵循：

- 模块宽度适配手机窄屏（最大 600px）
- 文字层级不超过 3 级（eyebrow / title / body）
- 颜色对比度满足 WCAG AA 标准（正文与背景对比度 ≥ 4.5:1）
- 模块间留白 ≥ 24px，避免视觉挤压

### 5.3 性能约束

微信公众号编辑器对 HTML 有严格限制，模块设计时规避：

- 不使用 JavaScript、`<script>`、`<iframe>`
- 不使用 `position: fixed`、`position: absolute`（破坏复制后样式）
- 不使用 `text-shadow`、`box-shadow`、`animation` 等会被编辑器剥离的属性
- 不使用 `linear-gradient`（在 `md2wechat.py` 的 `UNSUPPORTED_VALUE_KEYWORDS` 中被标记）
- 图片必须用 `<img>` 标签，不能用 `background-image`

### 5.4 可校验性

模块语法必须可被自动校验，阶段 4 校验项：

- 开始标记 `:::模块名` 中的模块名是否在 9 大类清单内
- 必填字段是否齐全
- 是否出现嵌套（禁止）
- 互斥模块是否重复出现
- 模块总数是否超过上限

---

## 六、与 styles/ CSS 的对应关系

### 6.1 三层 CSS 体系

模块的视觉样式由三层 CSS 协同决定：

| 层级 | 文件位置 | 作用范围 | 优先级 |
|------|---------|---------|--------|
| 模块基础样式 | [layout/modules-base.css](../layout/modules-base.css) | 所有模块的通用结构（`.module` 容器、`.module-header`、`.module-body`） | 最低 |
| 风格 CSS | [styles/](../styles/) 下各风格文件（如 `apple.md`、`cyber.md`） | 覆盖模块基础样式，注入风格配色 | 中 |
| Brand Profile 覆盖 | `~/.config/md2wechat/brand.md` 中声明的颜色与字号 | 全局品牌色覆盖 | 最高 |

### 6.2 模块到 CSS 类的映射

| 模块 | 主 CSS 类 | 关键子类 |
|------|---------|---------|
| `hero` | `.hero` | `.hero .eyebrow` / `.hero .title` / `.hero .subtitle` |
| `toc` | `.toc` | `.toc-item` / `.toc-index` |
| `cards` | `.cards` | `.card` / `.card-accent` |
| `steps` | `.steps` | `.step-item` / `.step-number` |
| `timeline` | `.timeline` | `.timeline-item` / `.timeline-dot` |
| `metrics` | `.metrics` | `.metric` / `.metric-value` |
| `compare` | `.compare` | `.compare-row` / `.compare-accent` |
| `verdict` | `.verdict` | `.verdict-title` / `.verdict-body` |
| `quote` | `.quote` | `.quote-text` / `.quote-source` |
| `cta` | `.cta` | `.cta-title` / `.cta-note` |
| `callout` | `.callout` | `.callout-tip` / `.callout-warning` / `.callout-note` / `.callout-important` |
| `highlight` | `.highlight` | `.highlight-title` |
| `author-card` | `.author-card` | `.author-name` / `.author-bio` |
| `brand-banner` | `.brand-banner` | `.brand-logo` / `.brand-slogan` |
| `checklist` | `.checklist` | `.check-item` / `.check-done` / `.check-pending` |
| `faq` | `.faq` | `.faq-item` / `.faq-question` |
| `split` | `.split` | `.split-left` / `.split-right` |
| `columns` | `.columns` | `.column-item` |
| `question` | `.question` | `.question-options` |
| `poll` | `.poll` | `.poll-options` |

### 6.3 风格覆盖规则

每种风格 CSS（`styles/{style}.md`）会通过 `#nice` 选择器覆盖模块默认配色：

- `apple` 风格：所有模块去边框、加圆角、用灰底卡片
- `cyber` 风格：模块加霓虹边框、暗黑底色、发光效果（仅装饰，实际渲染会被微信剥离）
- `tech-blog` 风格：模块用深蓝主色，左侧加竖线
- `tutorial` 风格：模块用薄荷绿主色，提示框加圆角

### 6.4 Brand Profile 覆盖

当 Brand Profile 中声明了 `主色调` / `辅助色` / `字号` 时，`md2wechat.py` 在生成 HTML 时会用 Brand Profile 的值覆盖风格 CSS 中对应的颜色和字号。详见 [brand-profile-spec.md](brand-profile-spec.md)。

---

## 七、扩展新模块的流程

如需新增一个模块，按以下步骤：

1. **明确归属**：确定该模块属于 9 大类中的哪一类，服务 4 件事中的哪一件
2. **定义字段**：列出必填字段和可选字段，给出字段说明
3. **写示例**：在 [layout/layout-modules.md](../layout/layout-modules.md) 中新增章节，提供至少一个完整示例
4. **加 CSS**：在 [layout/modules-base.css](../layout/modules-base.css) 中新增对应类名和默认样式
5. **加校验**：在 `md2wechat.py` 中新增模块名白名单、必填字段校验
6. **更新本文档**：在第二节模块清单中登记，在第四节组合规则中说明互斥关系
7. **加示例输出**：在 [examples/](../examples/) 中提供至少一篇使用该模块的示例文章

---

## 八、常见错误与对策

| 错误 | 后果 | 对策 |
|------|------|------|
| 模块名拼错（如 `:::Hero` 大写） | 转换脚本不识别，原样输出 | 模块名一律小写，参考第二节清单 |
| 缺必填字段（如 `hero` 缺 `title`） | 渲染出空模块 | 阶段 4 校验拦截，必填字段见 [layout-modules.md](../layout/layout-modules.md) |
| 模块嵌套 | 转换脚本解析异常 | 拆成并列模块，参考 3.3 节 |
| 单篇模块超过 7 个 | 视觉过载，读者跳出 | 按 4.5 节控制总数 |
| 互斥模块重复出现 | 品牌记忆点散失 | 按 4.1 / 4.4 节检查 |
| 使用 `linear-gradient` 等被剥离的属性 | 复制到公众号后样式丢失 | 改用纯色或边框装饰 |

---

> **参考**：模块字段细节见 [layout/layout-modules.md](../layout/layout-modules.md)，CSS 基础样式见 [layout/modules-base.css](../layout/modules-base.css)，公众号兼容性陷阱见 [wechat-traps.md](wechat-traps.md)。
