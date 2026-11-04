#!/usr/bin/env python3
"""validate_cases.py 的回归测试：钉住已修正的误报路径。

运行：python scripts/test_validate_cases.py
每条用例都对应一个真实踩过的坑，改动校验逻辑后必须全部通过。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_cases import check_case, check_suite, parse_cases  # noqa: E402


def run(md: str):
    cases = parse_cases(md)
    issues = []
    for c in cases:
        issues.extend(check_case(c))
    issues.extend(check_suite(cases, md, None))
    return cases, issues


def codes(issues) -> list[str]:
    return [i.code for i in issues]


GOOD = """### TC_PROFILE_NICKNAME_001: 修改昵称 - 输入合法值后列表显示新昵称

- 优先级: P0
- 类型: functional
- 来源: ai-generated
- 业务背景: 验证账号本人把昵称改为合法中文值并保存后列表同步显示

前置条件:
- 账号 A 已登录，处于「修改昵称」页

测试步骤:
1. 清空「昵称」输入框
2. 在「昵称」输入框输入 `测试用户`
3. 点击「保存」

业务结果:
- 账号列表页中账号 A 的「昵称」列显示 `测试用户`
"""


class TestParser(unittest.TestCase):
    def test_good_case_is_clean(self):
        _, issues = run(GOOD)
        self.assertEqual([i for i in issues if i.level == "error"], [])

    def test_table_mode_not_reported_as_missing_section(self):
        md = """### TC_NICK_002: 修改昵称 - 字符类型等价类

- 优先级: P2
- 类型: functional

| 用例 ID | 输入值 | 操作 | 预期结果 |
|---------|--------|------|----------|
| TC_NICK_002a | `测试用户` | 点击「保存」 | 「昵称」行显示 `测试用户` |
| TC_NICK_002b | `testuser` | 点击「保存」 | 「昵称」行显示 `testuser` |
"""
        _, issues = run(md)
        self.assertNotIn("FIELD_REQUIRED", codes(issues))

    def test_checkbox_lines_ignored(self):
        md = GOOD + "\n## 用例自检\n\n- [x] 业务结果无「正常」「正确」等评价词\n"
        _, issues = run(md)
        self.assertNotIn("VAGUE_WORD", codes(issues))


class TestFalsePositives(unittest.TestCase):
    def test_yanzhengma_is_not_verification_prefix(self):
        md = GOOD.replace(
            "修改昵称 - 输入合法值后列表显示新昵称",
            "验证码错误锁定 - 连续 5 次错误后账号锁定",
        )
        _, issues = run(md)
        self.assertNotIn("TITLE_PREFIX", codes(issues))

    def test_business_term_whitelist(self):
        md = GOOD.replace(
            "- 账号列表页中账号 A 的「昵称」列显示 `测试用户`",
            "- 订单状态为部分退款，剩余可退金额为 70.00 元",
        )
        _, issues = run(md)
        self.assertNotIn("VAGUE_WORD", codes(issues))

    def test_url_not_counted_as_long_sentence(self):
        md = GOOD.replace(
            "- 账号列表页中账号 A 的「昵称」列显示 `测试用户`",
            "- 详情页 Endpoint URL 为 https://example.com/hooks/orders 且状态为启用",
        )
        _, issues = run(md)
        self.assertNotIn("SENTENCE_LEN", codes(issues))

    def test_page_stay_is_valid_evidence(self):
        md = GOOD.replace(
            "- 账号列表页中账号 A 的「昵称」列显示 `测试用户`",
            "- 页面停留在登录页",
        )
        _, issues = run(md)
        self.assertNotIn("VAGUE_WORD", codes(issues))


class TestDetection(unittest.TestCase):
    def test_vague_word_detected(self):
        md = GOOD.replace(
            "- 账号列表页中账号 A 的「昵称」列显示 `测试用户`",
            "- 报表页面正常展示报表数据",
        )
        _, issues = run(md)
        self.assertIn("VAGUE_WORD", codes(issues))

    def test_title_prefix_detected(self):
        md = GOOD.replace(
            "修改昵称 - 输入合法值后列表显示新昵称", "验证昵称修改功能"
        )
        _, issues = run(md)
        self.assertIn("TITLE_PREFIX", codes(issues))

    def test_duplicate_id_detected(self):
        _, issues = run(GOOD + "\n" + GOOD)
        self.assertIn("ID_UNIQUE", codes(issues))

    def test_bad_id_format_detected(self):
        md = GOOD.replace("TC_PROFILE_NICKNAME_001", "TC_001")
        _, issues = run(md)
        self.assertIn("ID_FORMAT", codes(issues))

    def test_missing_required_section(self):
        md = GOOD.split("业务结果:")[0]
        _, issues = run(md)
        self.assertIn("FIELD_REQUIRED", codes(issues))

    def test_branch_in_step_detected(self):
        md = GOOD.replace(
            "3. 点击「保存」", "3. 如果按钮可点击则点击「保存」，否则刷新页面"
        )
        _, issues = run(md)
        self.assertIn("BRANCH_IN_STEP", codes(issues))

    def test_nonfunc_must_be_last(self):
        md = GOOD + GOOD.replace(
            "TC_PROFILE_NICKNAME_001", "TC_PROFILE_NICKNAME_002"
        ).replace("functional", "security") + GOOD.replace(
            "TC_PROFILE_NICKNAME_001", "TC_PROFILE_NICKNAME_003"
        )
        _, issues = run(md)
        self.assertIn("NONFUNC_TAIL", codes(issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
