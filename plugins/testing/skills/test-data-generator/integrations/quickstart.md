# 运行指南

## 环境与定位

使用 Python 3.11 或以上。根据实际安装位置设置 SKILL_ROOT；下面的仓库位置只适用于在 my-skills 根目录运行，复制安装后改为已安装的目录。

```bash
export SKILL_ROOT=plugins/testing/skills/test-data-generator
python -m venv /tmp/test-data-venv
/tmp/test-data-venv/bin/python -m pip install -r "$SKILL_ROOT/scripts/requirements.txt"
```

先检查现有环境；不要静默覆盖已有虚拟环境或安装全局依赖。Windows 使用对应虚拟环境的 `Scripts/python.exe`，实际支持情况以该宿主验证为准。

## 本地执行

```bash
/tmp/test-data-venv/bin/python "$SKILL_ROOT/scripts/run_data.py" inspect \
  --profile "$SKILL_ROOT/examples/order-member.yaml"
/tmp/test-data-venv/bin/python "$SKILL_ROOT/scripts/run_data.py" generate \
  --profile "$SKILL_ROOT/examples/order-member.yaml" --output-root /tmp/test-data-output
```

从 generate 输出复制实际 output_directory 再运行 validate：

```bash
/tmp/test-data-venv/bin/python "$SKILL_ROOT/scripts/run_data.py" validate \
  --profile "$SKILL_ROOT/examples/order-member.yaml" --dataset /tmp/test-data-output/实际运行目录
```

这是虚构示例，不执行订单或支付接口。具体业务修改项目 profile，运行位置采用用户指定目录或当前任务的独立临时目录。命令参数包含空格时保持引号，不把来源文本拼成 Shell 命令。

## 安全约束

- 生成文件不授权数据库写入、业务 API、Git 发布或基础设施操作；遵循目标项目原有授权要求。
- 输入仅使用允许的合成或脱敏资料，不保存真实账号、密码、Token、生产样本和凭据。sources 中的 reference 只记录定位，不自动访问链接。
- 依赖只安装到确认的项目或临时环境；配置不执行任意函数，不修改 Schema 检查来接受不支持项。
- 默认资源上限为总计十万条、100 MiB 输出、120 秒执行。生成和读取数据受限，重复生成使用新目录，不覆盖已有运行。
- 超限或中断保留失败记录，只处理本次创建的目录；数据校验通过不能描述为自动合规。

项目依赖、引擎版本和实际命令保存在交付证据中。无 Python 或无法运行时交付配置与说明，生成和验证保持 not_run。
