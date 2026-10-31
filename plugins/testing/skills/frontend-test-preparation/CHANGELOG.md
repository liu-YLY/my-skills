# Changelog

本文件记录 frontend-test-preparation 所有版本变更。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-10-31

### Added

- 纳入 testing plugin，作为 testing-bundle 第 8 个专业子 skill，承接链 9（前端测试准备 → 用例编写）
- 原样迁入入口与交接模板，保留分层导航索引、按变更增量维护、单需求映射与运行页面核实能力
- 补齐版本号、CHANGELOG 与评估用例，纳入版本同步与 CI 校验

### Boundaries

- 普通「测试前端功能」不触发本 skill，由 test-case-engineer 处理；本 skill 只在明确要求读前端代码、定位入口或维护页面索引时接入
- 运行页面核实需浏览器工具、测试环境与当次授权；缺少条件时只交付代码分析与待确认项，不把未执行标为通过
