"""Check review HTML, its embedded data, or the compact review-map format."""
import argparse
import json
import math
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


def index_rows(data, key):
    rows = data.get(key)
    if not isinstance(rows, list):
        raise ValueError(f"{key} 应为列表")
    indexed = {}
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"{key} 第 {number} 项应为对象")
        ident = row.get("id")
        if not isinstance(ident, str) or not ident.strip():
            raise ValueError(f"{key} 第 {number} 项缺少有效 ID")
        if ident in indexed:
            raise ValueError(f"{key} 中 ID 重复：{ident}")
        indexed[ident] = row
    return indexed


def check_refs(record, name, values, targets):
    if not isinstance(values, list):
        raise ValueError(f"{record} 的 {name} 应为列表")
    for target in values:
        if not isinstance(target, str) or target not in targets:
            raise ValueError(f"{record} 的 {name} 引用了不存在的 ID：{target}")
    if len(values) != len(set(values)):
        raise ValueError(f"{record} 的 {name} 中有重复关联")
    return set(values)


class ReviewDataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.active = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = dict(attrs).get("id") == "review-data"
            if self.active:
                self.blocks.append("")

    def handle_data(self, text):
        if self.active:
            self.blocks[-1] += text

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False


def load_data(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".html", ".htm"):
        parser = ReviewDataParser()
        parser.feed(text)
        if len(parser.blocks) != 1:
            raise ValueError("HTML 应包含唯一的 script#review-data")
        text = parser.blocks[0]
    return json.loads(text)


def strings(record, key, required=False):
    values = record.get(key)
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError(f"{record.get('id', '数据')} 的 {key} 应为字符串数组")
    if required and (not values or any(not v.strip() for v in values)):
        raise ValueError(f"{record.get('id', '数据')} 的 {key} 缺少内容")


def presentation(data):
    view = data.get("view")
    if view is None:
        lanes = data.get("lanes", [])
        if not isinstance(lanes, list):
            raise ValueError("lanes 应为列表")
        view = "rules" if "rules" in data else (
            "swimlane" if len(lanes) > 1 else "flow"
        )
    if view not in ("swimlane", "flow", "state", "rules"):
        raise ValueError("view 应为 swimlane、flow、state 或 rules")
    return view


def with_layout(data):
    view = presentation(data)
    result = {"nodes": [], "edges": [], "lanes": [], **data, "view": view}
    if view in ("flow", "state") and not result["lanes"]:
        columns = [node.get("lane") for node in index_rows(result, "nodes").values()]
        if any(type(column) is not int or column < 0 for column in columns):
            raise ValueError("单流程图和状态图的节点 lane 应为从 0 开始的列坐标")
        result["lanes"] = [{"name": ""} for _ in range(max(columns, default=0) + 1)]
    return result


def normalize_viewer(data):
    """Validate layout fields and adapt nested cases to the shared ID checks."""
    stages = index_rows(data, "stages")
    nodes = index_rows(data, "nodes")
    points = index_rows(data, "points")
    lanes = data["lanes"]
    if not stages or not isinstance(lanes, list):
        raise ValueError("样板需要至少一个环节，lanes 应为列表")
    if data["view"] == "rules" and (nodes or lanes or data["edges"]):
        raise ValueError("规则表使用 rules 记录条件与结果")
    if data["view"] != "rules" and (not lanes or not nodes):
        raise ValueError("业务图至少需要一个布局列和节点")
    if any(not isinstance(lane, dict) or not isinstance(lane.get("name"), str) for lane in lanes):
        raise ValueError("每条泳道应有 name 字符串")
    occupied = set()
    steps = []
    for ident, node in nodes.items():
        if not isinstance(node.get("title"), str) or not node["title"].strip() or not isinstance(node.get("note"), str):
            raise ValueError(f"{ident} 缺少节点 title 或 note")
        lane, row = node.get("lane"), node.get("row")
        if type(lane) is not int or not 0 <= lane < len(lanes) or type(row) is not int or row < 0:
            raise ValueError(f"{ident} 的 lane 或 row 超出有效范围")
        if (lane, row) in occupied:
            raise ValueError(f"{ident} 与其他节点占用相同的 lane、row")
        occupied.add((lane, row))
        if node.get("source") is not None:
            check_refs(ident, "source", [node["source"]], {**stages, **points})
        if "step" in node:
            steps.append(node["step"])
    if steps and (len(steps) != len(nodes) or
                  any(type(n) is not int or n <= 0 for n in steps) or
                  len(set(steps)) != len(steps)):
        raise ValueError("指定步骤号时，应给所有节点填写唯一正整数 step")

    if "__unmapped__" in points:
        raise ValueError("__unmapped__ 是未映射用例阅读区的保留 ID")
    mapped_points, cases = [], []
    for ident, point in points.items():
        if not isinstance(point.get("title"), str) or not point["title"].strip():
            raise ValueError(f"{ident} 缺少测试点 title")
        for field in ("context", "reminders"):
            strings(point, field)
        rules = point.get("rule")
        if not isinstance(rules, list) or not rules:
            raise ValueError(f"{ident} 缺少规则或待确认说明")
        for rule in rules:
            text = rule.get("text") if isinstance(rule, dict) else rule
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"{ident} 的 rule 应为文字或含 text 的规则对象")
        group = point.get("cases")
        if not isinstance(group, list):
            raise ValueError(f"{ident} 的 cases 应为列表，暂无用例时填空列表")
        mapped_points.append({**point, "stage_id": point.get("stage"), "node_ids": point.get("nodes", [])})
        for case in group:
            if not isinstance(case, dict):
                raise ValueError(f"{ident} 的用例应为对象")
            for field in ("pre", "steps", "expected"):
                strings(case, field, required=not case.get("deferred"))
            mapped = {**case, "point_ids": [ident]}
            if "nodes" in case:
                mapped["node_ids"] = case["nodes"]
            cases.append(mapped)

    orphan_cases = data.get("orphan_cases", [])
    if not isinstance(orphan_cases, list):
        raise ValueError("orphan_cases 应为列表")
    for case in orphan_cases:
        if not isinstance(case, dict) or not isinstance(case.get("unmapped_reason"), str) or not case["unmapped_reason"].strip():
            raise ValueError("未映射用例须说明 unmapped_reason")
        for field in ("pre", "steps", "expected"):
            strings(case, field, required=not case.get("deferred"))
        mapped = {**case, "point_ids": []}
        if "nodes" in case:
            mapped["node_ids"] = case["nodes"]
        cases.append(mapped)

    edges = data.get("edges")
    if not isinstance(edges, list):
        raise ValueError("edges 应为列表")
    adapted_edges = []
    for i, edge in enumerate(edges, 1):
        if not isinstance(edge, dict):
            raise ValueError(f"连线 {i} 应为对象")
        if "path" in edge or "labelAt" in edge:
            label = edge.get("labelAt")
            if (not isinstance(edge.get("path"), str) or not edge["path"].strip() or
                    not isinstance(label, list) or len(label) != 2 or
                    any(type(v) not in (int, float) or not math.isfinite(v) for v in label)):
                raise ValueError(f"连线 {i} 的 path 和 labelAt 应同时有效")
        adapted_edges.append({**edge, "from": edge.get("a"), "to": edge.get("b")})
    return {**data, "points": mapped_points, "cases": cases, "edges": adapted_edges}


def validate_anchors(data):
    """Check stable rule and transition references against their associated points."""
    points = index_rows(data, "points")
    mode = data["view"]
    if mode == "rules":
        anchors = index_rows(data, "rules")
        if not anchors:
            raise ValueError("规则表至少需要一条规则")
        stages = index_rows(data, "stages")
        for ident, row in anchors.items():
            check_refs(ident, "stage", [row.get("stage")], stages)
            strings(row, "conditions", required=True)
            if not isinstance(row.get("expected"), str) or not row["expected"].strip():
                raise ValueError(f"{ident} 缺少 expected")
        field = "rule_ids"
    elif mode == "state":
        anchors = index_rows({"edges": data["edges"]}, "edges")
        for ident, row in anchors.items():
            if not isinstance(row.get("label"), str) or not row["label"].strip():
                raise ValueError(f"{ident} 缺少状态转移条件 label")
        field = "transition_ids"
    else:
        return {}
    owners = {ident: check_refs(ident, "point_ids", row.get("point_ids", []), points)
              for ident, row in anchors.items()}
    for ident, point in points.items():
        inherited = {key for key, refs in owners.items() if ident in refs}
        check_case_anchors(point["cases"], field, anchors, inherited)
    check_case_anchors(data.get("orphan_cases", []), field, anchors, set())
    return owners


def check_case_anchors(cases, field, anchors, inherited):
    for case in cases:
        if field in case:
            mapped = check_refs(case["id"], field, case[field], anchors)
            if not mapped or not mapped <= inherited:
                raise ValueError(f"{case['id']} 的 {field} 应为所属测试点已关联目标的非空子集")


def validate_metadata(data):
    sources = index_rows({"sources": data.get("sources", [])}, "sources")
    for ident, source in sources.items():
        for key in ("title", "location"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise ValueError(f"{ident} 缺少来源 {key}")
        if "url" in source:
            url = source["url"]
            if (not isinstance(url, str) or not url.strip() or
                    urlsplit(url).scheme.lower() not in ("", "http", "https", "file")):
                raise ValueError(f"{ident} 的来源 url 不支持")
    records = list(data["nodes"]) + list(data["points"])
    if data["view"] == "rules":
        records.extend(data["rules"])
    if data["view"] == "state":
        records.extend({**edge, "title": edge["label"]} for edge in data["edges"])
    for point in data["points"]:
        records.extend(point["cases"])
        records.extend({**r, "id": point["id"] + " 的规则"} for r in point["rule"] if isinstance(r, dict))
    records.extend(data.get("orphan_cases", []))
    for record in records:
        ident = record.get("id", "记录")
        if "id" in record and "text" not in record and (not isinstance(record.get("title"), str) or not record["title"].strip()):
            raise ValueError(f"{ident} 缺少 title")
        state = record.get("fact_status")
        if state is not None and state not in ("documented", "inferred", "pending", "confirmed"):
            raise ValueError(f"{ident} 的 fact_status 不合法")
        refs = check_refs(ident, "source_ids", record.get("source_ids", []), sources)
        if state in ("confirmed", "documented") and not refs:
            raise ValueError(f"{ident} 标为已确认或资料事实时须有 source_ids")
        if "changed" in record and type(record["changed"]) is not bool:
            raise ValueError(f"{ident} 的 changed 应为布尔值")
        if "no_test_reason" in record and (not isinstance(record["no_test_reason"], str) or not record["no_test_reason"].strip()):
            raise ValueError(f"{ident} 的 no_test_reason 应说明理由")


def coverage_gaps(data, owners):
    """Report missing design relationships without claiming semantic coverage."""
    gaps = []
    def add(kind, ident, text, target):
        gaps.append({"kind": kind, "id": ident, "text": text, "target": target})
    mode = data["view"]
    anchored = set().union(*owners.values())
    linked = {n for point in data["points"] for n in point.get("nodes", [])}
    if mode == "state":
        linked.update(n for edge in data["edges"] if owners[edge["id"]] for n in (edge["a"], edge["b"]))
    if mode in ("rules", "state"):
        rows = data["rules"] if mode == "rules" else data["edges"]
        prefix, kind = ("r-", "rule") if mode == "rules" else ("t-", "transition")
        field = "rule_ids" if mode == "rules" else "transition_ids"
        by_point = index_rows(data, "points")
        for row in rows:
            ident = row["id"]
            label = row.get("title") or row["label"]
            if not owners[ident] and not row.get("no_test_reason"):
                add(kind + "_without_point", ident, label + "尚无关联测试点", prefix + ident)
            executable = [case for p in owners[ident] for case in by_point[p]["cases"] if not case.get("deferred")]
            if executable and not any(ident in case.get(field, [ident]) for case in executable):
                add(kind + "_without_case", ident, label + "尚无定位到此处的可执行用例", prefix + ident)
    incident = {n for edge in data["edges"] for n in (edge["a"], edge["b"])}
    for node in data["nodes"]:
        ident = node["id"]
        if ident not in linked and not node.get("no_test_reason"):
            add("node_without_point", ident, node["title"] + "尚无直接关联的测试点", "n-" + ident)
        if len(data["nodes"]) > 1 and ident not in incident:
            add("disconnected_node", ident, node["title"] + "与其他节点未连通", "n-" + ident)
    for point in data["points"]:
        ident = point["id"]
        if mode == "rules" and ident not in anchored:
            add("point_without_rule", ident, point["title"] + "尚未定位规则", "p-" + ident)
        if mode != "rules" and not point.get("nodes") and ident not in anchored:
            add("point_without_node", ident, point["title"] + "尚未定位流程 · " + point.get("unmapped_reason", ""), "p-" + ident)
        if not any(not case.get("deferred") for case in point["cases"]):
            add("point_without_case", ident, point["title"] + "尚无可执行用例", "p-" + ident)
    for case in data.get("orphan_cases", []):
        add("unmapped_case", case["id"], case["title"] + " · " + case["unmapped_reason"], "c-" + case["id"])
    return gaps


def validate(data, quiet=False):
    if not isinstance(data, dict):
        raise ValueError("输入应为 JSON 对象")
    viewer = any(key in data for key in ("lanes", "view", "rules"))
    anchor_owners = {}
    if viewer:
        original = with_layout(data)
        data = normalize_viewer(original)
        anchor_owners = validate_anchors(original)
        validate_metadata(original)
    stages, nodes, points, cases = (
        index_rows(data, key) for key in ("stages", "nodes", "points", "cases")
    )
    stage_owners = [("测试点", points)]
    if not viewer:
        stage_owners.append(("节点", nodes))
    for name, collection in stage_owners:
        for ident, row in collection.items():
            check_refs(f"{name} {ident}", "stage_id", [row.get("stage_id")], stages)

    edges = data.get("edges")
    if not isinstance(edges, list):
        raise ValueError("edges 应为列表")
    for i, edge in enumerate(edges, 1):
        if not isinstance(edge, dict):
            raise ValueError(f"连线 {i} 应为对象")
        for side in ("from", "to"):
            check_refs(f"连线 {i}", side, [edge.get(side)], nodes)

    point_nodes = {}
    unresolved = []
    anchored = set().union(*anchor_owners.values())
    for ident, point in points.items():
        mapped = check_refs(ident, "node_ids", point.get("node_ids", []), nodes)
        if not mapped and ident not in anchored and (not viewer or original["view"] != "rules"):
            if not str(point.get("unmapped_reason") or "").strip():
                raise ValueError(f"{ident} 未定位节点，请在 unmapped_reason 说明目前只能定位到环节或仍待确认")
            unresolved.append(ident)
        point_nodes[ident] = mapped

    for ident, case in cases.items():
        owners = check_refs(ident, "point_ids", case.get("point_ids"), points)
        if not owners and not str(case.get("unmapped_reason") or "").strip():
            raise ValueError(f"{ident} 未关联测试点，请说明 unmapped_reason")
        inherited = set().union(*(point_nodes[p] for p in owners))
        if "node_ids" in case:
            mapped = check_refs(ident, "node_ids", case["node_ids"], nodes)
            if owners and (not mapped or not mapped <= inherited):
                raise ValueError(f"{ident} 的分支应为所属测试点已关联节点的非空子集")

    gaps = coverage_gaps(original, anchor_owners) if viewer else []
    if not quiet:
        print(f"{len(stages)} 个环节，{len(nodes)} 个节点，{len(edges)} 条连线，"
              f"{len(points)} 个测试点，{len(cases)} 条用例记录。")
        for gap in gaps:
            print("待补充 " + gap["id"] + " · " + gap["text"])
        if not viewer and unresolved:
            print("尚未定位到具体节点：" + "、".join(unresolved))
    return gaps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping", type=Path)
    args = parser.parse_args()
    try:
        validate(load_data(args.mapping))
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
