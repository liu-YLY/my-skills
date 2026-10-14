# test-data-generator 行为与运行证据

这些文件来自实际独立任务执行及本机程序检查。完整说明见 [验证报告](../reports/2026-10-14-test-data-generator-verification.md)。

- [任务与检查标准](cases.json)：冻结 B01—B12、六项触发请求及 Skill 标识。
- [初轮结果](results.initial.jsonl) 和 [汇总](summary.initial.json)：两组各 35/36；B08 缺少用例来源追踪。
- [修订后结果](results.final.jsonl) 和 [汇总](summary.final.json)：保留其他初轮记录，以 B08 实际复跑替换有 Skill 组对应记录，得到 36/36；基线仍为 35/36。
- [证据索引](evidence-index.json)：原始收据、文件哈希、起始和最终 Skill 资源快照、本机大型产物位置。
- [有 Skill 原始证据](raw-evidence.with_skill.jsonl) 与 [基线原始证据](raw-evidence.baseline.jsonl)：逐文件保存原始命令、stdout/stderr、配置和报告文本及其 SHA256。JSONL 的 content 是原始 UTF-8 内容，可恢复原文件；不是重新生成的结果。
- responses 目录保存 37 份原始模型响应，结果文件以相对路径绑定它们，工具会核对字符数和哈希。
- [规模及重复哈希](scale-summary.json)、[最终引擎复核](final-artifact-revalidation.json)、[独立检查发现](forward-check-findings.json)、[修复复验断言](forward-check-assertions.json) 和 checks 目录保存程序证据。

汇总工具只验证输入、证据可读取性及统计，不执行模型任务。初轮是在实现期间执行，后续有选择复跑，不能把混合记录当成最终提交的全量盲测。耗时含工具往返和归档；基线 B10 只计归档窗口，触发判断另行复跑计时，因此不据此比较速度或 Token。

在仓库根目录复核保存的评分：

```bash
python scripts/skill-evals.py --skill test-data-generator \
  --cases-file docs/skill-evaluation/data-generator-2026-10-14/cases.json \
  --results docs/skill-evaluation/data-generator-2026-10-14/results.final.jsonl \
  --variants with_skill baseline --expected-runs 1
```

该命令无需访问本机大型数据目录即可核对已归档响应。索引中的大型数据和完整独立检查日志保存在本次本机的 `.venv-tools/data-generator/evidence/`，未纳入 Git；换机后要用 Skill 的示例重新生成。远程 CI、Linux/Windows 实际宿主及业务系统执行均为未执行。
