#!/usr/bin/env python3
"""validate_cases.py 的回归测试：钉住已修正的误报路径。

运行：python scripts/test_validate_cases.py
每条用例都对应一个真实踩过的坑，改动校验逻辑后必须全部通过。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_cases import check_case, check_suite, parse_cases, parse_yaml_cases  # noqa: E402


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

    def test_short_business_context_not_flagged(self):
        _, issues = run(GOOD)
        self.assertNotIn("BIZ_CONTEXT_LEN", codes(issues))


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

    def test_long_business_context_detected(self):
        md = GOOD.replace(
            "- 业务背景: 验证账号本人把昵称改为合法中文值并保存后列表同步显示",
            "- 业务背景: 验证在用户已完成登录且账号状态正常的前提下对昵称输入框输入超过长度限制的字符后点击保存系统给出校验提示",
        )
        _, issues = run(md)
        self.assertIn("BIZ_CONTEXT_LEN", codes(issues))

    def test_nonfunc_must_be_last(self):
        md = GOOD + GOOD.replace(
            "TC_PROFILE_NICKNAME_001", "TC_PROFILE_NICKNAME_002"
        ).replace("functional", "security") + GOOD.replace(
            "TC_PROFILE_NICKNAME_001", "TC_PROFILE_NICKNAME_003"
        )
        _, issues = run(md)
        self.assertIn("NONFUNC_TAIL", codes(issues))

    def test_preach_noise_detected_in_precond_and_result(self):
        md = GOOD.replace(
            "- 账号 A 已登录，处于「修改昵称」页",
            "- 账号 A 已登录，无其他阻断；已记录修改前快照，测试期间不手工修改数据库",
        ).replace(
            "- 账号列表页中账号 A 的「昵称」列显示 `测试用户`",
            "- 步骤 1～2：保存被拒，不用其他失败原因代替本例校验；前端置灰由体验用例另验",
        )
        _, issues = run(md)
        cs = codes(issues)
        self.assertIn("PREACH_NOISE", cs)
        self.assertIn("RESULT_STEP_PREFIX", cs)

    def test_checkpoint_step_prefix_still_valid_and_system_log_not_flagged(self):
        md = GOOD.replace(
            "业务结果:",
            "关键检查点:\n- 步骤 2 后：输入框显示 `测试用户`\n\n业务结果:\n- 审计日志已记录本次昵称变更事件",
        ).replace("- 账号列表页中账号 A 的「昵称」列显示 `测试用户`", "")
        _, issues = run(md)
        self.assertEqual([i for i in issues if i.level == "error"], [])

    def test_fictional_fixture_and_raw_db_col_detected(self):
        md = GOOD.replace(
            "- 账号 A 已登录，处于「修改昵称」页",
            "- 账号 A 额度充足（up_to=100, consume=81），隔离 stub 返回 503，见数据表 S1",
        )
        _, issues = run(md)
        cs = codes(issues)
        self.assertIn("RAW_DB_COL", cs)
        self.assertIn("FICTIONAL_FIXTURE", cs)

    def test_60_hanzi_and_two_semicolons_enforced_with_datagroup_exemption(self):
        md_two_semi = GOOD.replace(
            "- 账号 A 已登录，处于「修改昵称」页",
            "- 账号 A 已登录；处于修改昵称页；当前昵称为初始值",
        )
        _, issues = run(md_two_semi)
        self.assertIn("SENTENCE_LEN", codes(issues))

        long_line = "- " + "账号处于待激活状态且尚未绑定第三方登录方式并持有有效验证码" * 3
        md_long = GOOD.replace("- 账号 A 已登录，处于「修改昵称」页", long_line)
        _, issues_long = run(md_long)
        self.assertIn("SENTENCE_LEN", codes(issues_long))

        md_dg = GOOD.replace(
            "2. 在「昵称」输入框输入 `测试用户`",
            "2. 数据组：空字符串；纯空格；超过二十个汉字的超长测试输入内容样本一；特殊符号组合样本二；保留字样本三",
        )
        _, issues_dg = run(md_dg)
        self.assertNotIn("SENTENCE_LEN", codes(issues_dg))

    def test_yaml_cases_before_vs_after_depreach(self):
        bad_yaml = """
- id: "TC_ORDER_PAY_002"
  title: "[支付] 订单重复提交支付 - 拒绝第二次扣款"
  priority: "P1"
  type: "functional"
  description: |-
    追溯: 订单需求§支付幂等
    验证同一待支付订单重复发起支付时，仅扣款一次，防止重复扣费。
  preconditions:
    - "用户 A 正常未冻结，账户可用余额充足（balance=200），支付服务与账务服务可用，无风控或其他限流阻断"
    - "订单 ORD-01 处于待支付状态（pay_status=0, amount=100）；已记录支付前余额与流水快照，测试期间不手工修改订单状态"
  steps:
    - "用户 A 对订单 ORD-01 提交首次支付请求并完成支付"
    - "由技术协作者绕过页面防重按钮，直接向后端再次提交同一订单 ORD-01 的支付请求"
  expected_results:
    - "步骤 1：首次支付成功，订单变为已支付"
    - "步骤 2：第二次请求因订单已支付被拒绝，不用余额不足等其他失败原因代替本例幂等拦截；前端按钮置灰由体验用例另验"
  tags: [payment, idempotency]
"""
        bad_cases = parse_yaml_cases(bad_yaml)
        self.assertEqual(len(bad_cases), 1)
        bad_issues = check_case(bad_cases[0])
        bad_codes = codes(bad_issues)
        self.assertIn("PREACH_NOISE", bad_codes)
        self.assertIn("RAW_DB_COL", bad_codes)
        self.assertIn("RESULT_STEP_PREFIX", bad_codes)

        good_yaml = """
- id: "TC_UL_ACT_045"
  title: "激活流程满 30 分钟过期 - 未过期的重发码亦不可激活，重新登录后恢复"
  priority: "P1"
  type: "business"
  description: |-
    追溯: 统一登录前后端方案
    验证激活流程超过 30 分钟有效期后，未过期重发码不可激活，返回登录可取得新流程激活
  preconditions:
    - "主账号 A 待激活、未冻结，密码为 UlPass123"
    - "A 的原激活流程（有效期 30 分钟）在第 29 分钟重发过一次激活码；当前来到第 31 分钟，原激活流程已过期，但该重发码仍在 5 分钟有效期内且未使用"
  steps:
    - "在第 31 分钟查看原激活页面状态"
    - "绕过页面限制，直接向后端提交已过期的原激活流程与第 29 分钟那枚未过期的激活码"
    - "从过期提示页返回登录，用 A 的邮箱、密码 UlPass123 通过人机验证登录，获取新激活流程与新激活码"
    - "在有效期内提交新激活码完成激活"
  expected_results:
    - "原激活页显示流程已过期并提供返回登录入口，不再展示验证码输入框；A 仍为待激活状态"
    - "直接向后端提交过期流程与未过期激活码被拒（错误码 `1054008`），账号未激活、未新增登录记录"
    - "重新登录后取得新的 30 分钟激活流程并收到新激活码；提交新码后原账号 A 激活并登录成功，注册资料保留不变"
  tags: [credential-lifetime, account-activation, email-code]
"""
        good_cases = parse_yaml_cases(good_yaml)
        self.assertEqual(len(good_cases), 1)
        good_issues = check_case(good_cases[0]) + check_suite(good_cases, good_yaml, None)
        self.assertEqual([i for i in good_issues if i.level == "error"], [])

    def test_inline_section_header_parsed_properly(self):
        inline_md = """编排策略：策略一

### TC_WEBHOOK_ADD_001: 新增 Webhook - 填写合法 HTTPS 地址提交后持久化生效

- **优先级**: P0
- **类型**: functional
- **业务背景**: 验证管理员提交合法 HTTPS 地址可成功创建 Webhook

**前置条件**: 已登录管理员账号；已打开「Add webhook」弹窗

**测试步骤**:
1. 输入名称「订单通知」与地址 `https://example.com/hooks/orders`
2. 点击「Add webhook」提交并刷新列表页

**关键检查点**: 步骤 2 提交后：弹窗关闭，列表新增「订单通知」

**业务结果**: 刷新后「订单通知」仍存在且地址一致；列表仅新增 1 条记录

**后置条件**: 删除 Webhook「订单通知」

**标签**: webhooks, create
"""
        cases = parse_cases(inline_md)
        self.assertEqual(len(cases), 1)
        issues = check_case(cases[0]) + check_suite(cases, inline_md, None)
        self.assertEqual([i for i in issues if i.level == "error"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
