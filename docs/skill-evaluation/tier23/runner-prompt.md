# runner 指令模板（Tier 2/3 小规模对照）

runner 角色由 WorkBuddy 担任。两个 variant 的指令**严格分离**，尤其 no_skill 组不得引用任何 skill 指令内容。

---

## 模板 A：with_skill（加载 skill 指令）

```
你是「测试用例生成 runner」。请按下列步骤执行，不做额外发挥。

第一步：读取 skill 指令并按流程执行
- plugins/testing/skills/test-case-engineer/SKILL.md
- plugins/testing/skills/test-case-engineer/test-case-engineer-core.md
- 以及 SKILL.md 的「模式读取矩阵」所要求的 plugins/testing/skills/test-case-engineer/knowledge/ 下的 .md 文件
模式选择、流程裁剪、输出结构一律由 SKILL.md 自身路由规则决定。

第二步：对下面这条需求，独立地按 skill 指令生成测试用例集，写入指定文件（UTF-8 纯文本，不加 Markdown 代码围栏）

【严格约束】
1. 除文件路径与需求原文外，不附加任何写法要求；一切以 skill 指令文件自身规定为准。
2. 不读取 docs/skill-evaluation/ 目录下的任何 rubric、评测集 JSON、历史产物或报告；不读取 .workbuddy/ 记忆文件。
3. 不参考 docs/skill-evaluation/ 下任何既有 *-v*.txt 产物。

【需求原文】
{需求原文}

【输出文件】
docs/skill-evaluation/tier23/outputs/{case_id}-with_skill.txt
```

---

## 模板 B：no_skill（裸模型，不加载 skill）

```
你是「测试用例生成 runner」。你**没有**任何 skill 指令可参考，请直接根据需求本身生成测试用例集。

【需求原文】
{需求原文}

【输出文件】
docs/skill-evaluation/tier23/outputs/{case_id}-no_skill.txt

【要求】
1. 仅依据需求原文，用你通用能力生成一份完整、可执行的测试用例集。
2. 不要查找、不要引用、不要假设任何名为 test-case-engineer 的 skill 或知识文件。
3. 输出 UTF-8 纯文本，不加 Markdown 代码围栏。
```

> 关键点：no_skill 模板**只给需求原文**，明确禁止 runner 引用 skill，否则对照就失效了。

---

## 三条 case 的需求原文与 checks（供 runner 参考用，judge 判定时另给）

| case | 需求原文 | checks 条数 |
|---|---|---|
| #35 | 为「修改昵称」单字段功能编写测试用例。字段规则：长度 1–20 字符，允许中文、英文、数字，保存后列表与详情页同步显示。需求只涉及这一个字段，无跨模块联动。 | 4 |
| #37 | 需求含 5 条可测条目：手机号登录、验证码错误锁定、记住登录 7 天、退出登录、异地登录提醒。请编写用例并给出覆盖情况。 | 4 |
| #39 | 为 Webhook 创建功能编写用例，要求标题能独立定位测试点。界面控件为 Version 下拉框、Trigger 选择框、Endpoint URL 输入框、Add endpoint 按钮。 | 5 |

> runner 生成时不看 checks（避免给答案），checks 只给 judge。
