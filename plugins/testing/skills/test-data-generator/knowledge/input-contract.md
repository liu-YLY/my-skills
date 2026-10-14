# 输入协议

## 最小配置

profile 使用 YAML 或 JSON，协议版本 `1.0`。必须给出 `schema_version`、`profile_id`、`sources` 和 `entities`。实体包含数量、主键和字段，每个字段指定类型；生成数据时还必须指定生成器，校验已有数据时可省略。来源使用 `default_source_ids` 或对象自己的 `source_ids` 关联。

完整形状见 [配置 Schema](../schemas/profile.schema.json)，最小用法见 [基础字段示例](../examples/basic-fields.yaml)。标识符采用以字母开头的 ASCII 字母、数字、点、下划线或短横线，最多 64 字符。实体名还需在大小写不敏感的文件系统上互不冲突。引擎拒绝未知键、重复键、非有限值、未知引用及大于 1 MiB 的配置；深度最多 64、展开节点最多 20000，不接受 YAML 别名，不获取 sources 中的链接。数学上为整数的配置数值如 `3.0` 规范化为 Python 整数。

## 规则依据

来源类型为 `requirement`、`schema`、`code`、`user`、`sample` 或 `example`。sources 中保存定位和版本，不能保存凭据或真实用户数据。实体来源可被字段覆盖；规则、场景、关联和异常定义继承全局默认来源或显式指定。

确认状态使用 `confirmed`、`candidate`、`pending-confirmation`、`conflict`。明确提供的约定默认 confirmed；仅有 sample 来源的约束默认 candidate。不要为解除阻塞擅自把 candidate 改为 confirmed。

strict 模式阻止未确认约束，preview 模式保留这些约束并生成带 issues 的探索数据，校验状态为 incomplete。用户若只需要一个模块，应创建只包含该模块及其依赖的 profile，而不是删除其他模块的不确定项后宣称全项目规则明确。

## 字段和生成器

| 类型 | 数据表示 | 约束 |
|---|---|---|
| string | 字符串 | 长度、枚举、正则、空值、唯一性 |
| integer | JSON 整数，布尔值不算整数 | min、max、枚举、唯一性 |
| decimal | 普通十进制字符串，最多 64 字符，无指数 | min、max 使用字符串，scale 默认 2 |
| boolean | JSON true 或 false | 枚举和空值 |
| datetime | 带时区的 RFC 3339 字符串 | 条件比较、明确的生成时间窗口 |

每个字段必须存在，`nullable` 只决定是否允许 null；缺失字段只用于异常输入。主键不可空。`unique_keys` 定义复合唯一键，字段 `unique: true` 定义单字段唯一性；可空唯一键允许多个空值。

支持 constant、sequence、choice、integer、decimal、datetime_window、relative_datetime、reference、boundary、faker 十种生成器。integer 和 decimal 必须给出范围；choice 使用 values 或字段 enum，boolean 可省略 values。sequence 使用全实体记录位置生成，不在每个场景重新从头编号。

boundary 的 point 使用 min、max、min_length、max_length、empty 或 null，边界来自字段的明确约束；字符串 fill 默认 x，可指定一个字符。正常边界仍需合法，越界使用异常配方。faker 只支持 Schema 中的九种字符串 provider，必须给出 locale，并安装可选依赖；email 固定使用 example.invalid 域。姓名、电话和地址是合成值，仍需按项目格式检查，不能证明与真实人不存在偶然重合。

datetime_window 要求明确 reference_datetime；relative_datetime 依赖同记录另一个 datetime 字段。固定随机种子和时间基准后不要引入当前时间作为字段值。

## 关联与场景

父端必须为声明过的唯一键。复合引用按整组选择；部分为空不支持。子端关联字段使用 reference 或 constant；场景可固定其中部分字段以选择父键子集。重叠关系、循环依赖和任意联合约束求解不支持，不能隐藏这些限制。

`min_children` 和 `max_children` 约束每个父对象；max 为 null 表示无上限。普通同候选池分配维护剩余容量；部分固定字段使用分组容量匹配，保留复合键。无法满足匹配时报告 infeasible，候选预算或执行预算不足属于资源错误，不能当作数学无解。

scenarios 按 profile 顺序划分记录，数量之和必须等于对应实体数量。set 固定字段值，generators 覆盖字段生成方式；同一个字段不能同时使用两者。普通数据导入后保留这个记录顺序才能检查场景分布，不自动推断重叠场景。

已有测试矩阵的维度字段用 set 固定，辅助字段使用 choice 或 Faker，引用字段用 reference，计算字段使用明确生成器和独立规则。case_ids 保留用例编号，combination_id 保留输入矩阵编号，target_check_ids 声明场景必须实际检查的目标；本工具不生成 pairwise 矩阵。目标规则的条件始终不成立时，该场景为 incomplete。

规则使用有限条件和断言：eq、in、is_null、not_null、gte、lte、time_delta。有序比较只支持整数、十进制和时间；other_field 引用同记录相同逻辑类型的字段。time_delta 比较两个 datetime 的秒差，必须给出 min_seconds、max_seconds，可同时为 3600 表示精确一小时。每条规则有稳定 ID；自然语言规则不能假装已经成为机器检查。

无条件、同字段、字面量的 eq/in/gte/lte 会收窄生成域，不改变已声明约束。条件规则、字段间关系和聚合不自动求解；inspect 的 planned_rule_ids 与 validation_only_rule_ids 区分两者。缺少执行生成器不会妨碍 validate；生成容量与依赖检查只用于 generate。

## 异常输入

negative_scenarios 指定合法 base_scenario、数量、set/remove 变更和 expected_rule_violations。还可用 op: boundary 搭配 below_min、above_max、too_short、too_long；整数越界一步为 1，金额一步为声明 scale 的最小单位，字符串使用声明长度及 fill。缺边界时阻塞，不补业务阈值。引擎以原主键和位置保存基准引用，单样本替换基准记录校验，不把异常记录追加到正常集合。

自动检查 ID 在 inspect 的 check_ids 中，包括字段 `F-实体.字段-range`、`-type`、`-required` 等，主键 `K-实体-primary`、数量 `N-实体-count`。关联和业务规则使用声明 ID。先查看实际 ID，不编造不存在的预期违规。

异常校验不把基准人口场景分布当作单次 API 输入约束，但仍检查字段、唯一性、对象数量、业务及关联。预期系统响应另需契约；未提供时保持 pending-confirmation。
