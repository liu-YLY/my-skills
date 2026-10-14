# 生成与校验

运行方式和安装约束见 [运行指南](../integrations/quickstart.md)。

## 三个命令

inspect 加载、规范化和检查 profile，给出对象顺序、数量、检查 ID、来源问题和 profile_hash，不生成数据。generate 使用同一配置批量生成、独立校验、导出并重新读取复核。validate 对指定目录的实际文件运行检查，不信任旧报告里的 passed。

generate 的输出根目录每次产生一个独立运行子目录。结果包含 profile.normalized.json、generation-plan.json、data、negative/cases.jsonl、validation-report.json、report.md 和 manifest.json。失败留在 `.failed` 目录，manifest 标记 failed；不能把其中的半成品交付为完整数据。

CLI 在独立子进程中执行生成和校验，以工作时限终止耗时正则等阻塞操作；Python 解释器启动另设 10 秒上限。中断或超时保留本次运行的失败清单，其他目录内容保持完整。非有限 JSON 数值（NaN、Infinity）作为格式错误拒绝。

## 正常、边界和异常

正常和合法边界数据必须满足全部已确认规则。用场景明确指定关键边界及其数量，不把随机生成等同于边界覆盖。状态联动表示给定约定下的静态快照，不代表系统状态迁移或事件执行。

异常先使用通过数据检查的基准，再修改指定字段。预期违规集合与实际集合严格匹配；多出或缺少违规都算不匹配。类型错误使比较不可执行时记录 not_evaluable，不制造无意义的时间或金额比较错误。

金额保持 decimal 字符串，固定小数位数。输入字段类型、合法值和范围与异常输入的违规目的分别记录。修改场景或规则后重新生成，不能继续沿用旧基准数据的校验结论。

## 格式和重复生成

多格式导出使用同一批记录。JSON 和 JSONL 保留类型；CSV 用 `\N` 表示 null，字符串反斜线翻倍，因此空串、空值和字面 `\N` 可区分。整数和布尔值按 profile 恢复类型。外部导入工具必须采用相同约定或显式转换，不宣称通用于所有导入器。

validate 支持本工具的输出目录，也支持没有 manifest 的已有数据目录：按实体命名的 `.json`、`.jsonl` 或 `.csv` 文件可在目录本身或 data 子目录中。同一实体的多个格式必须一致。异常定义存在时还需要对应 negative/cases.jsonl。

种子、profile、引擎、Python 和依赖版本固定时，数据及异常样本文件可重复比较；运行 ID、耗时和 manifest 不属于相同字节的承诺。manifest 保存文件哈希和依赖版本，但文件仍需重新做语义检查。

## 结果解释

| 状态 | 含义 |
|---|---|
| generation complete | 本次文件交付完成，不代表业务数据合法 |
| validation passed | 声明范围内的数据与异常预期通过，导出和完整性检查通过 |
| validation incomplete | 存在候选或待确认规则，只能作为探索产物 |
| validation failed | 数据违规、异常不匹配、格式差异或完整性问题 |
| system execution not_run | 未导入数据库、调用 API 或执行业务测试 |

规则统计区分 declared、implemented、executed、适用记录数量和 not_evaluable。空实体或从未成立的条件不能当作充分的业务覆盖。错误明细默认最多 200 条，完整扫描和 error_count 不受明细截断影响。

必需检查没有执行时，unexecuted_checks 列出 ID，校验状态为 incomplete。允许空值的字段会记录其范围等约束不适用；条件始终为假的规则记录适用数为零，不宣称该条件分支被业务测试覆盖。

退出码：0 为命令成功；2 为配置、未确认规则或不支持项阻塞；3 为校验失败或 incomplete；4 为依赖、文件或资源运行错误。没有运行证据时保留 not_run，不把 inspect 成功当成 generate 成功。
