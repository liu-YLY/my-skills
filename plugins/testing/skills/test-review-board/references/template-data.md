# 用当前样板制作评审页

先创建独立的 `review.json`，在 skill 目录运行 `python3 scripts/render_review.py review.json --output review.html`。生成器校验数据，采用内置样板生成离线 HTML。输入错误会保留原输出；成功时原子替换目标文件。输入和输出须为不同路径，内置样板作为生成源保存。

样板可以离线打开，业务数据只在页面内部。里面的占位文字、角色和案例用于演示字段；制作时替换成当前项目内容。独立样板提供单业务域的阅读区，多域导航、全局搜索和修改记录按实际需求另外实现。生成器也可读取旧样板 HTML，用于迁移其中的业务数据。

## 数据对应关系

| 字段 | 用途与填写方式 |
| --- | --- |
| `title`、`context`、`intro`、`scope`、`status`、`provenance` | 页面名称、所属需求、一句话目标、范围、当前状态及来源说明。只写材料支持的事实。 |
| `view` | 填写 `swimlane`、`flow`、`state` 或 `rules`。旧样板省略时沿用泳道字段或规则表结构推定；状态图请显式指定。 |
| `lanes` | 泳道图的责任方数组，每项包含 `name` 和简短的 `note`。单流程图和状态图可省略，由节点列坐标确定画布。 |
| `stages` | 讲解环节，包含唯一 `id`、`title`、`note`。数组顺序决定导航顺序。 |
| `nodes` | 节点具有唯一 `id`、`title`、`note`、从 0 开始的列坐标 `lane` 和行坐标 `row`。流程节点可用 `behavior`、`support` 或 `branch`，状态图终态可用 `terminal`。同一坐标只放一个节点。规则表可省略。 |
| `nodes[].step` | 可选的稳定显示序号。沿用已有编号时，为所有节点填写唯一正整数；新图省略时样板自动计算。 |
| `nodes[].source` | 原节点的定位目标，可保留环节 ID 或测试点 ID。页面优先根据测试点的 `nodes` 找直接关联；没有直接关联时，使用此处的环节 ID 回退到该环节。实际资料来源写入 `provenance` 或对应规则说明。 |
| `edges` | 用 `a`、`b` 引用起终点，`label` 写触发条件，`alt` 为 true 时显示分支虚线。状态转移还需唯一 `id`，用 `point_ids` 关联测试点。自动连线发生遮挡时，可配对填写 SVG `path` 和坐标 `labelAt`。规则表可省略。 |
| `rules` | 规则表使用。每行含唯一 `id`、`title`、所属 `stage`、非空条件数组 `conditions`、业务结果 `expected`，以及所关联的 `point_ids`。可填写来源、状态和无需独立测试的理由。 |
| `points` | 每项有唯一 `id`、`title`、所属 `stage`，以及 `rule`、`context`、`reminders` 三个数组。`rule` 支持字符串和含 `text` 的来源状态对象，另两个为字符串数组。没有补充口径或提醒时用空数组。流程图使用 `nodes` 关联节点；规则或转移已关联时可省略。 |
| `points[].cases` | 此点下的用例数组，每项有全页唯一 `id`、`title` 和字符串数组 `pre`、`steps`、`expected`。暂无用例时填空数组，页面显示待补项。原用例数和顺序按输入保留。 |
| 用例的可选字段 | `nodes`、`rule_ids` 或 `transition_ids` 细分父点已关联的位置。`annotation` 保留口径，`deferred` 标记待删除，`summary` 标明步骤使用了已有业务摘要，`original_case` 可保留原始字段。 |
| `sources` | 可选来源数组，每项含 `id`、`title`、`location`。有材料链接时可填写 `url`，支持相对路径。来源通过 `source_ids` 引用。 |
| `fact_status`、`source_ids`、`changed` | 节点、测试点、用例和规则对象可增量标注事实状态、来源与本期变化。见 [覆盖缺口与来源依据](coverage-sources.md)。 |
| `orphan_cases` | 顶层未映射用例数组。用例字段与普通用例相同，另写 `unmapped_reason`，可选 `nodes`。其 ID 与全部普通用例共同唯一。 |
| `nodes[].no_test_reason` | 说明起止或交接节点为何无需独立测试点。 |
| `aliases` | 旧链接到新页面目标的映射。新页面用空对象，改版时保留还在使用的旧链接。 |
| `source`、`peer`、`md` 及各自的 `Label` 字段 | 原材料、其他页面及 Markdown 的入口。链接为空字符串时隐藏。可使用同目录相对路径。 |

文中已明确无法定位的测试点可以先保留 `nodes: []`，在 `context` 中说明缺口，页面按环节阅读。校验时用 `unmapped_reason` 记录同一原因。后续补齐来源后再恢复反向定位。

## 一个测试点下有两条不同分支的用例

下面假定节点 `check` 和 `decline` 已经存在，环节为 `redeem`。数量根据实际清单计算，示例中的 ID 只演示结构。

```json
{
  "id": "P-balance",
  "title": "余额刚好够与少一分",
  "stage": "redeem",
  "nodes": ["check", "decline"],
  "rule": ["兑换成本为100分，余额100分可以兑换，99分被拒绝。"],
  "context": [],
  "reminders": [],
  "cases": [
    {
      "id": "C-enough",
      "title": "余额100分时兑换成功",
      "nodes": ["check"],
      "pre": ["顾客余额100分，其他兑换条件均满足。"],
      "steps": ["兑换成本100分的券，刷新后查看余额和领券记录。"],
      "expected": ["余额为0，只新增一张券和一次扣分记录。"]
    },
    {
      "id": "C-short",
      "title": "余额99分时兑换被拒绝",
      "nodes": ["decline"],
      "pre": ["顾客余额99分，其他兑换条件均满足。"],
      "steps": ["尝试兑换成本100分的券，再查看余额和领券记录。"],
      "expected": ["余额仍为99，没有新增优惠券或扣分记录。"]
    }
  ]
}
```

标题行用于展开和收起卡片，独立的“定位流程”使用用例自己的 `nodes`。省略该字段时沿用父测试点的节点。一个用例跨多个测试点时，源记录仍按原 ID 维护；嵌入当前单归属样板前，要明确主要归属，并在其他点给出引用，或扩展映射以支持多归属。

## 保留链接和正文

页面目标支持 `#s-环节ID`、`#n-节点ID`、`#r-规则ID`、`#t-转移ID`、`#p-测试点ID`、`#cases-测试点ID`、`#c-用例ID`，反查使用 `#flow-p-测试点ID` 或 `#flow-c-用例ID`。当前范围和指定位置由样板自行写入后缀。延用旧 ID，避免无必要地重命名。当前实现使用 `~` 分隔范围，使用该字符的原 ID 应先建立独立的内部键并在正文保留原 ID。

前置、步骤和预期数组按纯文本渲染。遇到源材料中的表格、SQL 或多段步骤时，保留其内容，按需要扩展字段渲染并检查换行和横向滚动。固定生成器在写入数据区时会将 `<` 编码为 `\u003c`，保留原文并防止文本截断数据区。

先把明确的规则、用例字段和来源写完整，再做界面检查。原文件有完整步骤时，页面视觉调整仍沿用原步骤。只有用户要求压缩内容的场合才增加摘要，并保留原文入口。

## 检查实际输出

在 skill 目录运行 `python3 scripts/check_review_map.py /完整路径/评审页.html`。同一个命令也可读取样板数据 JSON；`assets/review-map.example.json` 则使用顶层 `cases` 的精简关系格式，脚本会分别识别。

可直接试跑 `python3 scripts/render_review.py assets/example-review.json --output /tmp/review-example.html`。该虚构示例包含两个细分分支、待补用例、未映射用例和来源状态。

规则表用 `python3 scripts/render_review.py assets/rules-example/review.json --output /tmp/order-export-rules.html` 生成，并把[示例来源](../assets/rules-example/rule-sources.md)放在 HTML 同目录。试读财务规则 R-03，打开共享测试点 TP-02，确认用例 TC-03 定位财务规则。切换到该点全部用例后，再确认 TC-02 定位运营规则 R-02。

结构通过后，在浏览器按 [用例查阅区设计](case-reader.md) 和 [泳道图取景与展示规则](swimlane-view.md)检查正常阅读路径。文字长度、跨行连线和恢复分支取决于具体数据，换了一套业务内容后仍要看一次真实页面。
