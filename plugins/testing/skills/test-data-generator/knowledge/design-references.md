# 设计参考

> **何时阅读**：需要了解本 skill 的能力取舍或方案来源时按需阅读；日常生成与校验无需加载。

- [Naodeng test-data-generation](https://github.com/naodeng/awesome-qa-skills/blob/main/skills/zh/testing-types/test-data-generation/SKILL.md)：吸收数据组的验收目标，落实为场景、目标检查、实际数量和用例映射。其 fixture 检查不替代本引擎执行证据。
- [Babysitter test-data-generation](https://github.com/a5c-ai/babysitter/blob/main/library/specializations/qa-testing-automation/skills/test-data-generation/SKILL.md)：吸收可复用工厂、Faker 与边界配方；业务默认值仍在项目 profile 中，未复制其数据库清空或当前时间种子示例。
- [Anh Tester test-data-generator](https://github.com/anhtester/codex-testing-kit/blob/main/.agents/skills/test-data-generator/SKILL.md)：区分固定组合维度、随机辅助字段、引用和计算字段；仅消费用户给定矩阵，不声称自动生成组合覆盖。
- [DAAF synthetic-data-workflow](https://github.com/DAAF-Contribution-Community/daaf/blob/main/.claude/skills/synthetic-data-workflow/SKILL.md)：借鉴分阶段独立核对与明确数据用途；未增加真实数据提取或隐私合成能力。
- [Faker](https://faker.readthedocs.io/en/master/#seeding-the-generator) 与 [Snowfakery](https://snowfakery.readthedocs.io/en/latest/index.html#unique-random-references)：参考独立随机实例、版本固定、配方和关联作用域；本工具仍使用声明协议与自己的有限容量匹配。

这些资料用于方案参考。第三方 Skill 的覆盖清单和代码示例不能作为本工具的模型效果、性能或业务验收证明。
