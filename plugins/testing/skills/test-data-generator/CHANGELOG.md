# Changelog

本文件记录 test-data-generator 所有版本变更。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.1.0] - 2026-10-14

### Added

- 支持项目规则配置、可重复关联造数、边界与异常配方、场景验收与独立文件校验
- 提供 inspect / generate / validate 工作流，覆盖 JSON、JSONL 与 CSV
- 明确系统执行边界：不写数据库、不调用业务接口、不执行压测，数据校验通过不代表系统测试通过

## [1.0.0] - 2026-10-14

- 初始版本，作为 testing-bundle 的离线测试数据方向子 skill
