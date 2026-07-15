# 高级排版模块规范

> **何时阅读**：阶段 3 排版时，当用户需要使用高级排版组件时必读。
> **覆盖范围**：`:::module` 语法规范、9 大类模块详解、渲染规则。
> **可跳过条件**：用户仅使用基础 Markdown 排版时跳过。

---

## 一、什么是高级排版模块

### 核心概念

**高级排版模块** = 一组预定义的视觉卡片组件，用 `:::模块名` 的语法写在 Markdown 里，渲染成精准的微信 HTML。

```markdown
:::hero
eyebrow: 深度观察
title: 公众号排版的真问题
subtitle: 不是好不好看，是读者读不读得完
:::
```

转换后变成一个有结构、有视觉层级的开篇卡片。

### 4 件事原则

每个模块只服务这 4 件事之一：

| 目的 | 解决什么 | 代表模块 |
|------|---------|---------|
| **attention** | 让读者先知道值不值得读 | hero, cards, verdict |
| **readability** | 让手机窄屏阅读不累 | toc, steps, part |
| **memorability** | 让读者记住一个判断或品牌 | verdict, manifesto, author-card |
| **conversion** | 让读者愿意收藏/关注/咨询/转发/购买 | cta, faq, checklist |

**核心原则**：选最少的模块，每件事做好一个。一篇文章 hero 只有一个，verdict 只有一个，cta 只有一个。不要堆模块。

---

## 二、语法规则

### 基本格式

每个模块使用 `:::模块名` 开始，`:::` 结束。

#### 字段格式 (fields)

```markdown
:::模块名
字段名: 字段值
:::
```

#### 行格式 (rows)，可带标题

```markdown
:::模块名[卡片标题]
行1 | 列2 | 列3
:::
```

#### 参数格式

```markdown
:::模块名{参数名=参数值}
内容
:::
```

### 九种正文格式

| 格式 | 正文形态 | 典型模块 |
|---|---|---|
| `fields` | 每行 `key: value` | `hero`、`verdict` |
| `rows` | 每行一条、列用 `\|` 分隔 | `toc`、`metrics` |
| `json_object` | 一个 JSON 对象 | `definition`、`tweet` |
| `json_array` | 一个 JSON 数组 | `stat-row`、`resource-list` |
| `markdown_images` | Markdown 图片列表 | `gallery-grid`、`svg-swipe-gallery` |
| `markdown_fields` | 重复字段组中允许 Markdown 图片 | `image-steps`、`figure-caption` |
| `split` | 两段正文由分隔线隔开 | `split` |
| `lines` | 逐行条目 | `flow`、`callout` |
| `dialogue` | 成对前缀或具名说话人行 | `question`、`dialogue-pair` |

---

## 三、9 大类模块详解

### 1. opening 开场类

**目的**：在读者决定读还是划走的 3 秒内，先给出判断。

#### hero — 开篇主视觉

**什么时候用**：文章开头第一屏，替代普通 H1 标题。适合观点文、产品发布、重大宣布。

**字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| eyebrow | ✅ | 标签词，如"深度观察"、"行业警告" |
| title | ✅ | 主标题，必须是一句判断或承诺 |
| subtitle | 可选 | 副标题，对主标题补一刀 |
| kicker | 可选 | 标题前的引导判断 |

**示例**：

```markdown
:::hero
variant: editorial
eyebrow: 深度观察
title: 高级排版服务阅读决策
subtitle: 主题决定气质，模块决定读者能不能看懂
:::
```

**不要这样用**：
- title 写成描述性句子（"本文介绍了...）而不是判断
- 在数据报告里用（改用 metrics）
- 一篇文章放两个 hero

---

#### toc — 阅读导航

**什么时候用**：文章超过 1500 字、有 3 个以上章节时，放在 hero 之后。

**格式**：`序号 | 章节名 | 一句话说明`

```markdown
:::toc[阅读导航]
01 | 问题定义 | 为什么现有排版让读者离开
02 | 模块原理 | 推荐模块各自解决什么
03 | 实战示例 | 一篇观点文的完整排版过程
:::
```

---

#### cards — 开篇卡片矩阵

**什么时候用**：文章结构清晰、有 3-4 个并列主题时，替代普通文字目录。

**格式**：`卡片标题 | 副标题 | 说明 | 颜色`（颜色：`accent` 或 `default`）

```markdown
:::cards[本文结构]
PART 01 | 问题 | 读者为什么不读你的文章 | accent
PART 02 | 原理 | 排版如何降低阅读决策成本 | default
PART 03 | 实战 | 推荐模块的选择逻辑 | default
PART 04 | 行动 | 今天就能上手的 3 步方法 | default
:::
```

---

#### part — 章节分隔

**什么时候用**：长文章的每个大章节开头，替代普通 `## 二级标题`。

**字段**：

```markdown
:::part
index: 02
title: 旧能力也要接进同一套系统
subtitle: 系统模块 · 列表 / 代码 / 表格
:::
```

---

#### label-title — 标签标题

**什么时候用**：短文或单主题文章的开篇，比 hero 轻量。

```markdown
:::label-title
label: 行业洞察
title: 公众号创作者正在经历什么
:::
```

---

### 2. infographic 信息图类

**目的**：把关键数据和结构用视觉方式呈现，让读者在窄屏里快速扫描。

#### metrics — 核心数据行

**什么时候用**：有 2-4 个横向并列的关键指标，比如数据报告、产品参数。

**格式**：`指标名 | 数值 | 说明 | 颜色`（颜色：`accent` 或 `default`）

```markdown
:::metrics[本次结果]
付费转化率 | 23% | 比上月提升 8 个百分点 | accent
平均阅读时长 | 4.2分钟 | 高于行业均值 1.8x | default
:::
```

---

#### compare — 对比行

**什么时候用**：有两种方案/时间点/方法需要横向对比时。

**格式**：`维度 | A方描述 | B方描述 | 颜色`

```markdown
:::compare[效果对比]
文章打开率 | 旧版排版 3.2% | 新版模块化排版 8.7% | accent
读者完读率 | 41% | 79% | default
制作时间 | 每篇 2小时 | 每篇 35分钟 | default
:::
```

---

#### steps — 步骤卡

**什么时候用**：有 3-6 步的线性流程，替代普通有序列表。

**格式**：`序号 | 步骤名 | 步骤说明`

```markdown
:::steps[落地步骤]
01 | 发现模块 | layout list 列出所有可用模块
02 | 查看规格 | layout show 确认字段和示例
03 | 写进文章 | 直接粘贴 :::module 语法
04 | 验证语法 | layout validate 检查错误
05 | 转换发布 | convert 输出微信 HTML
:::
```

---

#### timeline — 时间轴

**什么时候用**：有时间顺序的里程碑、发展历程、版本更新。

**格式**：`时间点 | 事件标题 | 事件说明`

```markdown
:::timeline[发展历程]
2023.01 | 初版上线 | 支持基础 Markdown 转换
2023.09 | 主题系统 | 推出 48 个专业主题
2024.03 | Prompt Catalog | AI 图片生成集成
2025.01 | Layout Catalog | 高级排版模块目录发布
:::
```

---

#### infographic — 单条信息图

**什么时候用**：需要突出单个数字、比例、或核心结论时。

**字段**：

```markdown
:::infographic
type: thesis
eyebrow: 核心判断
title: 高级排版不是装饰，是阅读决策系统
subtitle: 它先帮读者判断值不值得看，再帮作者建立记忆点
:::
```

`type` 的合法值：`thesis`、`number`、`contrast`、`formula`

---

### 3. judgment 判断类

**目的**：让读者记住作者的核心立场和判断，建立品牌认知。

#### verdict — 最终判断卡

**什么时候用**：观点文、复盘、方案结论，把你的核心判断单独拎出来。一篇文章只用一个。

**字段**：

```markdown
:::verdict
eyebrow: 最终判断
title: 真正的护城河不是模块数量，而是品牌表达系统
body: 每个模块必须服务一个真实的阅读任务，否则只是换皮。
note: 适合观点文、复盘、方案结论
:::
```

---

#### audience-fit — 读者匹配卡

**什么时候用**：文章开头明确适合谁读、不适合谁读，帮读者快速判断。

**字段**：`title` 为必填；`fit` 和 `avoid` 使用 `|` 分隔多项内容。

```markdown
:::audience-fit
title: 这篇适合谁
subtitle: 先帮读者判断要不要继续往下读
fit: 正在写长文的人 | 想建立个人品牌的人 | 需要稳定交付内容的人
avoid: 只发短讯的人 | 不需要结构化表达的人
:::
```

---

#### myth-fact — 认知纠偏

**什么时候用**：有需要打破的错误认知时，用"误区 vs 真相"的对比格式。

**格式**：`类型 | 内容`（类型：`myth` 或 `fact`）

```markdown
:::myth-fact
myth | 排版好看就是配色丰富
fact | 排版的本质是让读者更快做出阅读决策
myth | 模块越多，文章越专业
fact | 只用最少的模块，每件事做好一个
:::
```

---

#### manifesto — 宣言卡

**什么时候用**：品牌宣言、价值观声明、重大立场时。比 verdict 更有力量感。

**字段**：

```markdown
:::manifesto
label: 我的长期判断
title: 我相信普通人也应该拥有自己的内容系统
body: 排版系统的价值，是让不懂设计的人也能稳定输出有识别度的文章。
believe: 结构先于风格 | 文字永远是主角 | 主题负责气质
against: 大字报式排版 | 随机堆模板 | 为装饰牺牲阅读
:::
```

---

#### bridge — 转场

**什么时候用**：两个章节之间需要过渡，承上启下。

**字段**：

```markdown
:::bridge
label: 下一段为什么重要
title: 看完判断后，必须看到证据
body: 没有证据的观点只是态度，下一段用数据和案例把它撑住。
next: 继续看证据模块
:::
```

---

### 4. evidence 证据类

**目的**：用数据、案例、图片支撑你的判断，让读者相信你说的是真的。

#### quote — 引用卡

**什么时候用**：引用他人观点、用户反馈、书中金句时，给出来源。

**字段**：`quote` 是必填引用内容，`source` 是来源。

```markdown
:::quote
variant: light
eyebrow: 核心观点
quote: 模块帮助读者更快找到判断、证据和下一步。
source: 内容设计原则
:::
```

---

#### image-annotate — 图片标注

**什么时候用**：需要用 1-3 条编号说明解读图片时，如截图分析、海报拆解。

**字段**：

```markdown
:::image-annotate
eyebrow: 图片解读
title: 一张图配三条编号说明，关系更清楚
image: https://example.com/annotate.png
alt: 图片解读卡示例
point: 01 | 主信息区 | 一进入页面先看到的核心判断和主标题
point: 02 | 指标区 | 适合讲关键数字、结果和变化
:::
```

`point` 格式是 `编号 | 标题 | 描述`；描述可省略。至少写 1 条，最多读取 3 条。

---

#### image-compare — 图片对比

**什么时候用**：需要展示前后对比、A/B 测试结果时。

**字段**：

```markdown
:::image-compare
eyebrow: 前后对比
title: 左右并排时，变化会比大段解释更直接
left_title: 改版前
left_image: https://example.com/before.png
right_title: 改版后
right_image: https://example.com/after.png
:::
```

---

#### image-steps — 图片步骤

**什么时候用**：操作教程，每步配一张截图。

**格式**：每组使用 `step` 和 `desc`，中间可放一张 Markdown 图片。

```markdown
:::image-steps{columns=2 caption_style=numbered}
step: 打开编辑器
![打开](https://example.com/open.jpg)
desc: 选择主题和文章结构。
note: 先确认文章目标
step: 复制到微信
![复制](https://example.com/copy.jpg)
desc: 检查预览后复制。
:::
```

---

#### image-text — 图文并排

**什么时候用**：需要图片配合文字说明时，图文左右排列。

**字段**：

```markdown
:::image-text
layout: right
eyebrow: 功能截图
title: 图和说明绑在一起，读者更容易跟上重点
body: 左边先讲结论，右边再放真实界面，减少来回对照的成本。
image: https://example.com/split.png
alt: 图文双栏示例图片
:::
```

---

### 5. conversion 行动类

**目的**：文章读完之后，让读者做一件事（收藏、关注、咨询、转发、购买）。

#### cta — 行动召唤

**什么时候用**：文章结尾，引导读者采取行动。一篇文章只用一个。

**字段**：

```markdown
:::cta
title: 如果你想把公众号做成稳定可复用的结构，可以从这套模块开始。
note: 联系作者咨询 API 服务
:::
```

---

#### faq — 常见问题

**什么时候用**：有 3-8 个读者经常问的问题，或者需要处理潜在疑虑时。

**格式**：`问题 | 回答`

```markdown
:::faq[常见问题]
这些模块只能在某个主题里用吗？ | 不是，48 个专业主题都支持高级排版模块。
API 模式和 AI 模式有什么区别？ | API 模式直接转换输出 HTML，AI 模式生成提示词给外部 AI。
我的文章需要用几个模块？ | 按 4 件事原则选，hero 1 个，verdict 1 个，cta 1 个，不要堆。
:::
```

---

#### checklist — 清单

**什么时候用**：有操作性清单、检查事项时，比普通列表更有视觉重量。

**格式**：`状态 | 描述 | 说明`（状态：`done`、`pending`、`warn`、`todo`）

```markdown
:::checklist[发布前检查]
done | 结构先搭好 | 先把目录、重点和结论摆出来
pending | 数据再补齐 | 关键数字和案例放进对应模块
warn | 链接和说明单独检查 | 避免手机里出现跳读和看不清
:::
```

---

#### cases — 案例卡

**什么时候用**：有 2-4 个真实案例或客户背书时。

**格式**：`案例名 | 行业 | 结果描述`

```markdown
:::cases[使用案例]
某科技公众号 | 科技媒体 | 使用模块化排版后，平均完读率从 41% 提升到 79%
某教育公众号 | 在线教育 | 读者停留时长增加 2.3 倍
:::
```

---

### 6. brand 品牌类

**目的**：建立品牌识别度，让读者一眼认出你的文章。

#### author-card — 作者卡片

**什么时候用**：文章结尾，展示作者信息和社交媒体。

**字段**：

```markdown
:::author-card
name: 张三
title: 资深技术博主
bio: 10 年技术写作经验，专注公众号排版优化
avatar: https://example.com/avatar.png
wechat: techblog_zhang
:::
```

---

#### brand-banner — 品牌横幅

**什么时候用**：文章开头或结尾，展示品牌标识和口号。

**字段**：

```markdown
:::brand-banner
logo: https://example.com/logo.png
name: 技术干货分享
slogan: 让复杂技术变得简单易懂
:::
```

---

### 7. sprint4 精选增强类

**目的**：提供更丰富的视觉效果和交互体验。

#### callout — 提示框

**什么时候用**：需要强调重要信息、警告或提示时。

**格式**：`类型 | 内容`（类型：`tip`、`warning`、`note`、`important`）

```markdown
:::callout
tip | 这个技巧可以让你的文章阅读量提升 50%
:::
```

---

#### highlight — 高亮块

**什么时候用**：需要突出显示关键数据或结论时。

**字段**：

```markdown
:::highlight
eyebrow: 关键数据
title: 转化率提升 23%
body: 通过优化排版结构和视觉层级，读者完读率显著提升。
:::
```

---

### 8. free-layout 自由布局类

**目的**：提供更灵活的布局选项。

#### split — 左右分栏

**什么时候用**：需要并排展示两部分内容时。

**格式**：两段正文由 `---` 分隔线隔开。

```markdown
:::split
左侧内容：这是左边的说明文字
---
右侧内容：这是右边的说明文字
:::
```

---

#### columns — 多列布局

**什么时候用**：需要 2-4 列并排展示内容时。

**参数**：`columns=2` 或 `columns=3` 或 `columns=4`

```markdown
:::columns{columns=2}
第一列内容
---
第二列内容
:::
```

---

### 9. interactive 交互类

**目的**：增加读者参与度和互动性。

#### question — 互动问题

**什么时候用**：文章中间或结尾，引导读者思考或评论。

**字段**：

```markdown
:::question
title: 你在公众号排版中遇到的最大挑战是什么？
options: 视觉设计 | 内容结构 | 读者互动 | 技术实现
:::
```

---

#### poll — 投票

**什么时候用**：需要收集读者意见或偏好时。

**字段**：

```markdown
:::poll
title: 你更喜欢哪种排版风格？
options: 技术博客风 | 教程指南风 | 深度干货风 | 轻松聊天风
:::
```

---

## 四、模块选择指南

### 按文章类型选择

| 文章类型 | 推荐模块组合 |
|---------|-------------|
| 观点文 | hero + verdict + cta |
| 数据报告 | hero + metrics + compare + cta |
| 教程 | hero + steps + callout + faq |
| 产品发布 | hero + features + cases + cta |
| 经验分享 | hero + timeline + quote + cta |

### 按目的选择

| 目的 | 推荐模块 |
|------|---------|
| 吸引注意力 | hero, cards, label-title |
| 提高可读性 | toc, steps, part |
| 建立记忆点 | verdict, manifesto, highlight |
| 促进转化 | cta, faq, checklist |

---

## 五、渲染规则

### 模块解析流程

1. 识别 `:::模块名` 开始标记
2. 读取模块内容直到 `:::` 结束标记
3. 根据模块类型解析字段或行数据
4. 应用对应的 CSS 样式渲染

### 错误处理

- 未知模块名：输出警告，保留原始文本
- 缺少必填字段：输出错误提示，建议补充
- 语法格式错误：尝试自动修复，无法修复时保留原始文本

### 兼容性

- 所有模块都支持微信公众号编辑器
- 图片模块需要用户提供有效图片链接
- 交互模块在公众号中显示为静态内容

---

## 六、最佳实践

### 模块数量控制

- 一篇文章最多使用 5-7 个模块
- hero、verdict、cta 各最多 1 个
- 避免连续使用多个视觉重量相近的模块

### 内容适配

- 确保模块内容与文章主题相关
- 不要用模块填充空白内容
- 每个模块都应该提供实际价值

### 视觉平衡

- 注意模块间的视觉重量平衡
- 避免在短段落后放置重型模块
- 合理使用留白和分隔线

---

> **参考**：完整示例见 [examples/](../examples/) 目录
