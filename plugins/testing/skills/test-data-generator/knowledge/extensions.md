# 扩展边界

当前版本只生成和检查本地文件。业务规则由项目 profile 定义；字段格式正确、外键存在和已声明规则通过，不代表系统实际接受记录。

## 不支持项

- 任意表达式、Shell、SQL 或从配置动态加载函数。
- 自动求解循环依赖、重叠关联和任意多约束组合。
- 跨表求和、库存守恒、复杂计费、签名和密码初始化。
- 按任意正则自动生成字符串；正则只用于已生成值的检查。
- XLSX、SQL 导出，数据库导入、真实 API 造数、压测和状态迁移执行。

遇到这些要求时先说明缺少哪种能力和影响范围。可以整理项目扩展接口或独立脚本方案，不能删除规则后声称完整校验，也不能把“不支持”改成“已通过”。

## 项目扩展

复杂业务算法留在项目的 test-data 配置与代码中。适配器需要明确版本、输入、生成或转换方式、独立检查和可重复条件；执行外部系统时另需环境、资源追踪、失败处理、清理与授权。

只有多个实际任务重复需要同一能力时，才考虑增加通用算子。先用正反样例验证，再扩展协议版本、Schema、引擎、测试和说明，避免把订单或物流特例写进全局规则。

本 Skill 可读取已有用例或状态模型中的明确造数目标，但不重做完整测试策略。缺少其他 Skill 时，仍可根据明确 profile 独立运行。

## 设计参考

- [Naodeng test-data-generation](https://github.com/naodeng/awesome-qa-skills/blob/main/skills/zh/testing-types/test-data-generation/SKILL.md)：吸收数据组的验收目标，落实为场景、目标检查、实际数量和用例映射。其 fixture 检查不替代本引擎执行证据。
- [Babysitter test-data-generation](https://github.com/a5c-ai/babysitter/blob/main/library/specializations/qa-testing-automation/skills/test-data-generation/SKILL.md)：吸收可复用工厂、Faker 与边界配方；业务默认值仍在项目 profile 中，未复制其数据库清空或当前时间种子示例。
- [Anh Tester test-data-generator](https://github.com/anhtester/codex-testing-kit/blob/main/.agents/skills/test-data-generator/SKILL.md)：区分固定组合维度、随机辅助字段、引用和计算字段；仅消费用户给定矩阵，不声称自动生成组合覆盖。
- [DAAF synthetic-data-workflow](https://github.com/DAAF-Contribution-Community/daaf/blob/main/.claude/skills/synthetic-data-workflow/SKILL.md)：借鉴分阶段独立核对与明确数据用途；未增加真实数据提取或隐私合成能力。
- [Faker](https://faker.readthedocs.io/en/master/#seeding-the-generator) 与 [Snowfakery](https://snowfakery.readthedocs.io/en/latest/index.html#unique-random-references)：参考独立随机实例、版本固定、配方和关联作用域；本工具仍使用声明协议与自己的有限容量匹配。

这些资料用于方案参考。第三方 Skill 的覆盖清单和代码示例不能作为本工具的模型效果、性能或业务验收证明。
