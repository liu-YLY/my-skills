#!/usr/bin/env python3
"""测试用例静态校验器（D 类规则）。

只校验可布尔判定的规则：格式、枚举、必填、词表、句长、结构、编排。
不做语义判断——覆盖度、可判定性、业务合理性交给评审 agent。

规则权威源：knowledge/writing-rules.md、test-standards.md、case-arrangement.md
用法：
    python scripts/validate_cases.py <file.md|dir> [--json] [--strict] [--budget N]
退出码：0 无 error；1 有 error；2 参数或解析错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 规则元数据
# tier: D=可布尔判定（本脚本负责） / J=需语义判断（评审 agent 负责）
RULES: dict[str, tuple[str, str, str]] = {
    # code: (中文名, tier, 默认级别)
    "ID_FORMAT": ("ID 格式", "D", "error"),
    "ID_UNIQUE": ("ID 唯一", "D", "error"),
    "ID_SEQ": ("ID 序号连续", "D", "warning"),
    "FIELD_REQUIRED": ("必填字段", "D", "error"),
    "ENUM_PRIORITY": ("优先级枚举", "D", "error"),
    "ENUM_TYPE": ("类型枚举", "D", "error"),
    "ENUM_SOURCE": ("来源枚举", "D", "error"),
    "ENUM_REVIEW": ("审核状态枚举", "D", "error"),
    "TITLE_PREFIX": ("标题不以验证/测试开头", "D", "error"),
    "TITLE_SEPARATOR": ("标题分隔符", "D", "warning"),
    "TITLE_LEN": ("标题长度", "D", "warning"),
    "VAGUE_WORD": ("模糊表达", "D", "error"),
    "SENTENCE_LEN": ("句长超限", "D", "error"),
    "PLACEHOLDER": ("占位话术", "D", "error"),
    "BRANCH_IN_STEP": ("步骤内分支", "D", "error"),
    "STEP_VERB": ("步骤缺动作", "D", "warning"),
    "BIZ_CONTEXT_PREFIX": ("业务背景前缀", "D", "warning"),
    "POSTCOND_VAGUE": ("后置条件模糊", "D", "error"),
    "CHECKPOINT_FORMAT": ("检查点格式", "D", "warning"),
    "STEP_GROUP": ("步骤分块", "D", "warning"),
    "BODY_LEN": ("正文长度", "D", "warning"),
    "TAG_FORMAT": ("Tag 格式", "D", "warning"),
    "TAG_COUNT": ("Tag 数量", "D", "warning"),
    "ARRANGE_DECLARE": ("编排策略声明", "D", "warning"),
    "NONFUNC_TAIL": ("非功能用例置末尾", "D", "warning"),
    "CASE_BUDGET": ("用例数预算", "D", "warning"),
    "DUP_TITLE": ("标题同模块重复", "D", "warning"),
    "FILE_FORMAT": ("文件用例格式无法解析", "D", "error"),
}

PRIORITIES = {"P0", "P1", "P2", "P3"}
# 本脚本不判定的 J 类规则：须由异源评审 agent 执行。
# 显式列出，避免把「0 error」误读成「质量达标」。
J_RULES = [
    ("业务结果可判定性", "执行人能否据此判 pass/fail"),
    ("测试点覆盖度", "7 维度扫描是否完整落为用例"),
    ("术语全文一致", "同一概念是否全文只有一个说法"),
    ("步骤可执行性", "照做即可执行，无需追问"),
    ("预期与步骤对应", "是否存在 steps 未发生操作的断言"),
    ("拆分合并合理性", "是否混入独立目标，或该合未合"),
    ("优先级业务依据", "P0-P3 是否由业务影响推导"),
]

TYPES = {
    "functional", "ui", "security", "performance",
    "compatibility", "usability", "accessibility", "observability",
}
SOURCES = {"ai-generated", "manual", "ai-reviewed"}
REVIEW_STATES = {"not-reviewed", "reviewed"}
NONFUNC = {"performance", "security", "compatibility", "usability", "accessibility", "observability", "ui"}

REQUIRED_META = ["优先级", "类型"]
REQUIRED_SECTIONS = ["测试步骤", "业务结果"]

# 明确不可执行的模糊表达（几乎不可能是合法业务术语）
VAGUE_STRONG = [
    "符合预期", "结果正确", "配置正确", "功能正常", "应生效", "与测试目标一致",
    "错误信息", "非法字符", "按测试点要求执行", "执行对应操作", "验证相关功能",
    "相关信息", "相关功能", "对应操作", "进行配置", "填写相关信息",
]
# 需结合语境判断，交由 warning
VAGUE_WEAK = [
    "超长", "边界值", "非法值", "多次", "一些", "部分", "大量", "少量",
    "随机", "任意", "特殊", "频繁", "大约", "左右", "上下", "缺省", "很多",
    "一段时间", "一会", "适量", "某些", "超小", "超短", "过低", "过高",
    "多于", "少于", "一定范围", "各模块", "设备无异常", "计数正常",
]
# 「明确业务术语不因包含单字违规」——writing-rules.md 明示的例外
TERM_WHITELIST = (
    "部分退款", "部分成功", "部分失败", "部分取消",
    "默认值", "默认套餐", "默认配置", "正常订单", "正常状态",
    "边界值测试", "边界值分析", "最小权限", "最大长度", "所有角色",
)
# 「结果正常」「显示正确」这类谓语式模糊
VAGUE_PATTERN = re.compile(
    r"(结果|显示|功能|页面|提示|返回|状态|配置|操作|文案|响应)"
    r"(正常|正确|符合预期|无误)"
)


def _mask_terms(text: str) -> str:
    for w in TERM_WHITELIST:
        text = text.replace(w, "×" * len(w))
    return text

STEP_VERBS = (
    "输入 点击 选择 勾选 打开 关闭 刷新 填写 清空 提交 保存 删除 修改 新增 创建 "
    "上传 下载 拖拽 滚动 切换 取消 返回 查询 访问 调用 发送 接收 等待 复制 粘贴 "
    "重命名 移除 启用 禁用 展开 收起 登录 退出 进入 设置 调整 确认 拒绝 查看 观察 "
    "长按 双击 右键 悬停 移动 导入 导出 绑定 解绑 授权 撤销 恢复 重置 重试 并发 "
    "断开 连接 记录 截取 抓取 监听 抓包 核对 比较 模拟 注入 拦截 绕过 构造 重复 "
    "限制 遍历 搜索 筛选 排序 分页 加载 渲染 断言 提取 折叠 拖入 替换 "
    "下发 计算 发起 触发 执行 获取 读取 写入 解析 组装 拼接 变更 置为 赋值 跳转"
).split()
STEP_LEAD_OK = STEP_VERBS + ["在", "将", "把", "对", "从", "以", "用", "为", "重复", "再次", "连续"]

EXPECT_EVIDENCE = (
    "显示 展示 出现 消失 跳转 返回 变为 写入 更新 保持 置灰 可点击 不可点击 "
    "包含 等于 为空 非空 提示 弹窗 报错 成功 失败 数量 条 值 状态 字段 列表 "
    "响应 日志 记录 新增 删除 变更 生效 标记 灰 禁用 启用 高亮 选中 "
    "停留 位于 处于 仍在 仍为 不变 未变 页面 内容 可见 隐藏 折叠 展开 置顶"
).split()

HEAD_RE = re.compile(r"^(#{3,4})\s+(TC_[A-Za-z0-9_]+)\s*[:：]\s*(.+?)\s*$")
META_RE = re.compile(r"^-\s*\*{0,2}([^\*:：]{2,12})\*{0,2}\s*[:：]\s*(.*)$")
SECTION_RE = re.compile(r"^\*{0,2}(前置条件|测试步骤|业务结果|预期结果|关键检查点|后置条件|标签)\*{0,2}\s*[:：]?\s*$")
ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*\S)\s*$")
ID_RE = re.compile(r"^TC_([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)_(\d{3})([a-z]?)$")
TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"^\s*```")


@dataclass
class Case:
    cid: str
    title: str
    line: int
    meta: dict[str, tuple[str, int]] = field(default_factory=dict)
    sections: dict[str, list[tuple[int, str]]] = field(default_factory=dict)
    section_order: list[str] = field(default_factory=list)
    table_rows: list[tuple[int, str]] = field(default_factory=list)

    def sec(self, name: str) -> list[tuple[int, str]]:
        if name == "业务结果" and name not in self.sections:
            return self.sections.get("预期结果", [])
        return self.sections.get(name, [])


CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+")
QUOTED_RE = re.compile(r"「[^」]*」|『[^』]*』|“[^”]*”|\"[^\"]*\"")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.\-/]*")
NUM_RE = re.compile(r"\d+")
CHECKBOX_RE = re.compile(r"^[-*]\s*\[[ xX]\]")
SUBLABEL_RE = re.compile(r"^\*\*[^*]{2,20}\*\*\s*[:：]?\s*$")
TABLE_ROW_RE = re.compile(r"^\|\s*(TC_[A-Za-z0-9_]+)\s*\|(.+)\|\s*$")
TC_ID_RE = re.compile(r"TC_[A-Za-z0-9_]+")
# 评审型产出的特征词：出现 5 次以上且无用例块时，判定为评审报告而非用案例集
REVIEW_HINT_RE = re.compile(r"(评审|审查|问题|建议|维度|结论|整改|不合格|合格|扣分)")
SKIP_NAME_RE = re.compile(
    r"(no_skill|baseline|control|report|plan|comparison|audit|guide|readme|changelog"
    r"|overview|notes|verification)",
    re.I,
)


@dataclass
class Issue:
    code: str
    line: int
    cid: str
    msg: str
    evidence: str = ""
    file: str = ""

    @property
    def level(self) -> str:
        return RULES[self.code][2]

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "rule": RULES[self.code][0],
            "tier": RULES[self.code][1],
            "level": self.level,
            "file": self.file,
            "line": self.line,
            "case": self.cid,
            "message": self.msg,
            "evidence": self.evidence,
        }


def _strip_noise(text: str) -> str:
    """剥离代码、URL、引号内文案与白名单业务术语——它们是数据，不是表达问题。"""
    t = CODE_RE.sub("", text)
    t = URL_RE.sub("", t)
    t = QUOTED_RE.sub("", t)
    return _mask_terms(t)


def _measure(text: str) -> int:
    """中文表达的有效字数：排除代码、URL、英文标识符与数字。"""
    t = _strip_noise(text)
    t = ASCII_TOKEN_RE.sub("", t)
    t = NUM_RE.sub("", t)
    return len(re.sub(r"\s+", "", t))


def parse_cases(text: str) -> list[Case]:
    lines = text.splitlines()
    cases: list[Case] = []
    cur: Case | None = None
    section: str | None = None
    in_fence = False

    for idx, raw in enumerate(lines, start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            if cur is not None and section:
                m = ITEM_RE.match(raw)
                if m:
                    cur.sections.setdefault(section, []).append((idx, m.group(1)))
            continue

        head = HEAD_RE.match(raw)
        if head:
            cur = Case(cid=head.group(2), title=head.group(3), line=idx)
            cases.append(cur)
            section = None
            continue
        if cur is None:
            continue

        sec = SECTION_RE.match(raw.strip())
        if sec:
            name = sec.group(1)
            if name == "预期结果":
                name = "业务结果"
            section = name
            cur.sections.setdefault(name, [])
            if name not in cur.section_order:
                cur.section_order.append(name)
            continue

        if raw.strip().startswith("## ") or raw.strip().startswith("# "):
            cur = None
            section = None
            continue

        stripped = raw.strip()
        if CHECKBOX_RE.match(stripped) or stripped.startswith(">"):
            continue
        if SUBLABEL_RE.match(stripped):
            section = None
            continue

        table = TABLE_ROW_RE.match(stripped)
        if table:
            cur.table_rows.append((idx, stripped))
            continue

        meta = META_RE.match(raw)
        if meta:
            key = meta.group(1).strip()
            value = meta.group(2).strip().strip("*")
            if key in ("前置条件", "测试步骤", "业务结果", "预期结果", "关键检查点", "后置条件"):
                section = "业务结果" if key == "预期结果" else key
                cur.sections.setdefault(section, [])
                if value:
                    cur.sections[section].append((idx, value))
            else:
                cur.meta[key] = (value, idx)
                section = None
            continue

        if section:
            m = ITEM_RE.match(raw)
            if m:
                cur.sections.setdefault(section, []).append((idx, m.group(1)))
    return cases


def check_case(c: Case) -> list[Issue]:
    out: list[Issue] = []

    def add(code: str, line: int, msg: str, evidence: str = "") -> None:
        out.append(Issue(code, line, c.cid, msg, evidence[:80]))

    # ID 格式
    m = ID_RE.match(c.cid)
    if not m:
        add("ID_FORMAT", c.line, f"ID `{c.cid}` 不符合 TC_{{模块}}_{{功能}}_{{三位序号}}", c.cid)

    # 必填
    for k in REQUIRED_META:
        if k not in c.meta or not c.meta[k][0]:
            add("FIELD_REQUIRED", c.line, f"缺少必填字段「{k}」")
    for k in REQUIRED_SECTIONS:
        if not c.sec(k):
            if c.table_rows and k in ("测试步骤", "业务结果"):
                continue
            add("FIELD_REQUIRED", c.line, f"缺少必填段落「{k}」")

    # 枚举
    pri = c.meta.get("优先级", ("", c.line))
    if pri[0] and pri[0] not in PRIORITIES:
        add("ENUM_PRIORITY", pri[1], f"优先级 `{pri[0]}` 不在 P0-P3", pri[0])
    typ = c.meta.get("类型", ("", c.line))
    if typ[0] and typ[0] not in TYPES:
        add("ENUM_TYPE", typ[1], f"类型 `{typ[0]}` 不在 8 类枚举内", typ[0])
    src = c.meta.get("来源", ("", c.line))
    if src[0] and src[0] not in SOURCES:
        add("ENUM_SOURCE", src[1], f"来源 `{src[0]}` 不在 ai-generated/manual", src[0])
    rv = c.meta.get("人工审核状态", ("", c.line))
    if rv[0] and rv[0] not in REVIEW_STATES:
        add("ENUM_REVIEW", rv[1], f"审核状态 `{rv[0]}` 不在 not-reviewed/reviewed", rv[0])

    # 标题
    t = c.title.strip()
    if re.match(r"^(验证(?!码)|测试(?!数据|环境|账号|用例))", t):
        add("TITLE_PREFIX", c.line, "标题不以「验证」「测试」开头", t)
    if " - " not in t and "－" not in t:
        add("TITLE_SEPARATOR", c.line, "标题缺少「 - 」分隔被测对象与行为", t)
    if _measure(t) > 40:
        add("TITLE_LEN", c.line, f"标题 {_measure(t)} 字，超过 40 字软上限", t)

    # 业务背景前缀
    bg = c.meta.get("业务背景")
    if bg and not bg[0].startswith("验证"):
        add("BIZ_CONTEXT_PREFIX", bg[1], "业务背景未以「验证」开头", bg[0])

    # Tag
    tag = c.meta.get("标签")
    if tag:
        tags = [x.strip() for x in re.split(r"[,，\s]+", tag[0]) if x.strip()]
        for x in tags:
            if not TAG_RE.match(x):
                add("TAG_FORMAT", tag[1], f"Tag `{x}` 不是小写 kebab-case", x)
        if not 1 <= len(tags) <= 5:
            add("TAG_COUNT", tag[1], f"Tag 数量 {len(tags)}，应为 1-5", tag[0])

    # 步骤
    steps = c.sec("测试步骤")
    for line, text in steps:
        plain = _strip_noise(text)
        if re.search(r"\bif\b|\belse\b|如果.*(则|那么|否则)|若.*(则|否则)|否则", plain, re.I):
            add("BRANCH_IN_STEP", line, "步骤内含条件分支，应拆为独立用例", text)
        for w in VAGUE_STRONG:
            if w in plain:
                add("VAGUE_WORD", line, f"步骤含模糊表达「{w}」", text)
                break
        for w in VAGUE_WEAK:
            if w in plain:
                add("VAGUE_WORD", line, f"步骤含待具体化表达「{w}」", text)
                break
        if VAGUE_PATTERN.search(plain):
            add("VAGUE_WORD", line, "步骤用「正常/正确」代替可观察结果", text)
        if not (plain.startswith(tuple(STEP_LEAD_OK)) or any(v in plain for v in STEP_VERBS)):
            add("STEP_VERB", line, "步骤缺少明确动作动词", text)
        for w in ("按测试点要求执行", "执行对应操作", "验证相关功能", "填写相关信息", "进行配置"):
            if w in plain:
                add("PLACEHOLDER", line, f"占位话术「{w}」", text)
                break

    # 业务结果
    results = c.sec("业务结果")
    for line, text in results:
        plain = _strip_noise(text)
        for w in VAGUE_STRONG:
            if w in plain:
                add("VAGUE_WORD", line, f"业务结果含模糊表达「{w}」", text)
                break
        for w in VAGUE_WEAK:
            if w in plain:
                add("VAGUE_WORD", line, f"业务结果含待具体化表达「{w}」", text)
                break
        if VAGUE_PATTERN.search(plain):
            add("VAGUE_WORD", line, "业务结果用评价词代替可观察事实", text)

    # 句长
    for name in ("测试步骤", "业务结果"):
        for line, text in c.sec(name):
            plain = _strip_noise(text)
            if _measure(plain) > 100:
                add("SENTENCE_LEN", line, f"单句 {_measure(plain)} 字，超过 100 字", text)
            for clause in re.split(r"[，,、]", plain):
                if _measure(clause) > 40:
                    add("SENTENCE_LEN", line, f"逗号构件 {_measure(clause)} 字，超过 40 字必须改写", text)
                    break

    # 检查点格式
    for line, text in c.sec("关键检查点"):
        if not re.match(r"^步骤\s*\d+\s*后\s*[:：]", text):
            add("CHECKPOINT_FORMAT", line, "检查点应为「步骤 N 后：…」", text)

    # 后置条件
    for line, text in c.sec("后置条件"):
        if re.search(r"环境(恢复)?正常|无需处理|无异常", text):
            add("POSTCOND_VAGUE", line, "后置条件写评价而非可执行动作", text)

    # 步骤分块
    if len(steps) > 7:
        grouped = any(re.match(r"^\s*(准备|提交|校验|执行|清理|初始化|前置)", t) for _, t in steps)
        if not grouped:
            add("STEP_GROUP", steps[0][0], f"{len(steps)} 个步骤超过 7 条且未按业务阶段分块")

    # 正文长度
    body_len = sum(_measure(text) for _, t in steps + results for text in [t])
    if body_len > 300:
        add("BODY_LEN", c.line, f"正文 {body_len} 字，超过 300 字建议", "")

    # 紧凑表格模式
    for line, text in c.table_rows:
        cells = [x.strip() for x in text.strip("|").split("|")]
        if len(cells) < 3:
            add("FIELD_REQUIRED", line, "紧凑表格行少于 3 列（ID/操作/预期）", text)
        joined = _strip_noise(" ".join(cells))
        for w in VAGUE_STRONG + VAGUE_WEAK:
            if w in joined:
                add("VAGUE_WORD", line, f"表格行含模糊表达「{w}」", text)
                break

    return out


def check_suite(cases: list[Case], text: str, budget: int | None) -> list[Issue]:
    out: list[Issue] = []

    # ID 唯一
    seen: dict[str, int] = {}
    for c in cases:
        if c.cid in seen:
            out.append(Issue("ID_UNIQUE", c.line, c.cid, f"ID 重复，首次出现于第 {seen[c.cid]} 行"))
        else:
            seen[c.cid] = c.line

    # 序号递增（只查同前缀内的逆序/重号；起点不查，样本常为节选）
    groups: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for c in cases:
        m = ID_RE.match(c.cid)
        if m:
            groups[m.group(1)].append((int(m.group(2)), c.cid))
    for prefix, items in groups.items():
        items.sort()
        for (prev, prev_cid), (num, cid) in zip(items, items[1:]):
            if num <= prev:
                out.append(Issue("ID_SEQ", 0, cid, f"{prefix} 序号非递增：{prev_cid}({prev:03d}) → {cid}({num:03d})"))

    # 标题同模块重复
    titles: dict[str, str] = {}
    for c in cases:
        key = re.sub(r"\s+", "", c.title)
        if key in titles:
            out.append(Issue("DUP_TITLE", c.line, c.cid, f"标题与 {titles[key]} 重复", c.title))
        else:
            titles[key] = c.cid

    # 编排策略声明
    if cases and not re.search(r"(用户旅程|模块分组|编排策略|策略一|策略二)", text):
        out.append(Issue("ARRANGE_DECLARE", 1, "-", "用例集未声明编排策略（用户旅程 / 模块分组）"))

    # 非功能用例置末尾
    flags = []
    for c in cases:
        typ = c.meta.get("类型", ("", 0))[0]
        flags.append(typ in NONFUNC)
    if any(flags):
        last_func = max((i for i, f in enumerate(flags) if not f), default=-1)
        first_non = min((i for i, f in enumerate(flags) if f), default=-1)
        if first_non < last_func:
            out.append(Issue(
                "NONFUNC_TAIL", cases[first_non].line, cases[first_non].cid,
                "非功能类型用例未统一置于末尾（应独立成组追加）",
            ))

    # 预算
    if budget and len(cases) > budget:
        out.append(Issue("CASE_BUDGET", cases[budget].line, "-", f"共 {len(cases)} 条，超出预算 {budget} 条"))

    return out


def collect_targets(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(
            p for p in target.rglob("*")
            if p.suffix.lower() in (".md", ".txt", ".markdown") and p.is_file()
        )
    raise SystemExit(f"路径不存在：{target}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="测试用例静态校验器（D 类规则）")
    ap.add_argument("target", help="用例文件或目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="warning 也视为失败")
    ap.add_argument("--budget", type=int, default=None, help="用例数预算上限")
    ap.add_argument(
        "--mode", choices=["auto", "generate", "review"], default="auto",
        help="auto=按内容判断（默认）；generate=强制按用例格式校验；review=跳过用例格式检查",
    )
    ap.add_argument("--quiet", action="store_true", help="只输出统计")
    ap.add_argument("--max-print", type=int, default=40, help="最多打印多少条明细")
    args = ap.parse_args(argv)

    files = collect_targets(Path(args.target))
    all_issues: list[Issue] = []
    report = []

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = f.read_text(encoding="utf-8", errors="ignore")
        cases = parse_cases(text)
        issues: list[Issue] = []
        if not cases:
            is_review = len(REVIEW_HINT_RE.findall(text)) >= 5
            if args.mode == "review" or (args.mode == "auto" and is_review):
                continue  # 评审报告的正文是评审结论，不适用用例块格式
            tc_count = len(TC_ID_RE.findall(text))
            if tc_count >= 3 and not SKIP_NAME_RE.search(f.name):
                it = Issue(
                    "FILE_FORMAT", 1, f.name,
                    f"含 {tc_count} 处用例标识但无「### TC_xxx: 标题」块，整份文件未被任何规则校验；"
                    f"改用 `### TC_模块_功能_序号: 标题` 承载每条用例",
                )
                it.file = str(f)
                issues.append(it)
            else:
                continue
        else:
            for c in cases:
                issues.extend(check_case(c))
            issues.extend(check_suite(cases, text, args.budget))
            for it in issues:
                it.file = str(f)
                if it.cid == "-":
                    it.cid = f.name
        all_issues.extend(issues)
        report.append({"file": str(f), "cases": len(cases), "issues": len(issues)})

    errors = [i for i in all_issues if i.level == "error"]
    warns = [i for i in all_issues if i.level == "warning"]
    total_cases = sum(r["cases"] for r in report)

    if args.json:
        print(json.dumps({
            "summary": {
                "files": len(report),
                "cases": total_cases,
                "errors": len(errors),
                "warnings": len(warns),
                "failed": bool(errors) or (args.strict and bool(warns)),
            },
            "by_file": report,
            "by_rule": dict(Counter(i.code for i in all_issues).most_common()),
            "unchecked_j_rules": [{"rule": n, "criterion": c} for n, c in J_RULES],
            "issues": [i.as_dict() for i in all_issues],
        }, ensure_ascii=False, indent=2))
    else:
        if not args.quiet:
            shown = all_issues[: args.max_print]
            cur_file = None
            for it in shown:
                print(f"{'ERROR' if it.level == 'error' else 'WARN ':5} "
                      f"{it.code:18} L{it.line:<5} {it.cid}\n"
                      f"      → {it.msg}" + (f"  ⏎ {it.evidence}" if it.evidence else ""))
            if len(all_issues) > len(shown):
                print(f"... 另有 {len(all_issues) - len(shown)} 条未显示（--max-print 调整）")

        print("\n" + "─" * 62)
        print(f"文件 {len(report)}  用例 {total_cases}  ERROR {len(errors)}  WARN {len(warns)}")
        if all_issues:
            print("规则命中：")
            for code, n in Counter(i.code for i in all_issues).most_common(12):
                name, tier, _ = RULES[code]
                print(f"  {n:>4}  {code:18} {name}")
        if total_cases:
            print("未覆盖（J 类，需评审 agent）：")
            for n, c in J_RULES:
                print(f"      {n}：{c}")
            print("提示：0 error 仅代表 D 类规则通过，不代表用例质量达标。")
        print("─" * 62)

    failed = bool(errors) or (args.strict and bool(warns))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
