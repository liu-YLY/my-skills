"""Run from the skill directory with python3 -m unittest discover -s tests -v."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_review_map import load_data, validate, ReviewDataParser
from render_review import render


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = load_data(ROOT / "assets/example-review.json")

    def test_gaps_are_visible_and_do_not_block_draft(self):
        content, gaps = render(self.data)
        self.assertEqual({g["kind"] for g in gaps}, {"node_without_point", "point_without_case", "unmapped_case"})
        parser = ReviewDataParser()
        parser.feed(content)
        loaded = json.loads(parser.blocks[0])
        self.assertEqual(loaded["coverage_gaps"], gaps)
        self.assertEqual(loaded["points"][2]["cases"], [])
        self.assertEqual(loaded["orphan_cases"], self.data["orphan_cases"])

    def test_case_branch_is_a_subset(self):
        _, gaps = render(self.data)
        self.assertTrue(gaps)
        self.data["points"][0]["cases"][1]["nodes"] = ["apply"]
        with self.assertRaisesRegex(ValueError, "非空子集"):
            render(self.data)

    def test_legacy_template_without_metadata(self):
        data = load_data(ROOT / "assets/swimlane-review.html")
        render(data)
        self.assertNotIn("fact_status", data["points"][0])

    def test_original_compact_map_still_valid(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validate(load_data(ROOT / "assets/review-map.example.json"))

    def test_missing_source_reference_and_unsupported_fact_claim(self):
        self.data["points"][0]["source_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "不存在"):
            render(self.data)
        self.data["points"][0]["source_ids"] = []
        with self.assertRaisesRegex(ValueError, "须有 source_ids"):
            render(self.data)

    def test_no_test_reason_and_disconnected_nodes(self):
        self.data["nodes"][-1]["no_test_reason"] = "在上游已验证取消结果"
        self.data["nodes"].append(dict(id="detached", title="分离的历史入口", note="", kind="support", lane=0, row=8))
        _, gaps = render(self.data)
        self.assertFalse(any(g["id"] == "cancel" and g["kind"] == "node_without_point" for g in gaps))
        self.assertTrue(any(g["id"] == "detached" and g["kind"] == "disconnected_node" for g in gaps))

    def test_deferred_cases_do_not_fill_coverage(self):
        self.data["points"][1]["cases"][0]["deferred"] = True
        _, gaps = render(self.data)
        self.assertTrue(any(g["id"] == "P2" and g["kind"] == "point_without_case" for g in gaps))

    def test_rules_without_a_diagram_report_only_rule_and_case_gaps(self):
        data = load_data(ROOT / "assets/rules-example/review.json")
        self.assertEqual([(g["kind"], g["id"]) for g in validate(data, quiet=True)],
                         [("point_without_case", "TP-03")])
        for case in data["points"][1]["cases"]:
            case["rule_ids"] = ["R-02"]
        self.assertIn(("rule_without_case", "R-03"),
                      {(g["kind"], g["id"]) for g in validate(data, quiet=True)})
        data["points"][1]["cases"][0]["rule_ids"] = ["R-01"]
        with self.assertRaisesRegex(ValueError, "rule_ids.*非空子集"):
            render(data)

    def test_state_transitions_can_be_the_only_point_anchor(self):
        self.data["view"] = "state"
        point = self.data["points"][0]
        point["nodes"] = []
        for i, edge in enumerate(self.data["edges"]):
            edge.update(id=f"T-{i}", label=edge.get("label") or "执行操作")
        self.data["edges"][0]["point_ids"] = [point["id"]]
        for case in point["cases"]:
            case.pop("nodes", None)
            case["transition_ids"] = ["T-0"]
        _, gaps = render(self.data)
        self.assertNotIn(("point_without_node", point["id"]), {(g["kind"], g["id"]) for g in gaps})
        point["cases"][0]["transition_ids"] = ["T-1"]
        with self.assertRaisesRegex(ValueError, "transition_ids.*非空子集"):
            render(self.data)

    def test_flow_layout_uses_node_columns_without_actors(self):
        self.data["view"] = "flow"
        del self.data["lanes"]
        content, _ = render(self.data)
        parser = ReviewDataParser()
        parser.feed(content)
        generated = json.loads(parser.blocks[0])
        self.assertEqual(generated["nodes"], self.data["nodes"])
        self.assertEqual(len(generated["lanes"]), 1 + max(n["lane"] for n in generated["nodes"]))
        self.assertTrue(all(not lane["name"] for lane in generated["lanes"]))

    def test_all_points_can_be_empty(self):
        self.data["points"] = []
        _, gaps = render(self.data)
        self.assertTrue(any(g["kind"] == "node_without_point" for g in gaps))

    def test_unique_case_ids_include_orphans(self):
        self.data["orphan_cases"][0]["id"] = "C1"
        with self.assertRaisesRegex(ValueError, "重复"):
            render(self.data)

    def test_source_text_cannot_break_the_data_script(self):
        value = '</script><script src="https://invalid.example/a.js">bad()</script>'
        self.data["title"] = value
        self.data["points"][0]["cases"][0]["steps"] = [value]
        content, _ = render(self.data)
        self.assertNotIn('<script src=', content)
        parser = ReviewDataParser()
        parser.feed(content)
        self.assertEqual(len(parser.blocks), 1)
        self.assertEqual(json.loads(parser.blocks[0])["points"][0]["cases"][0]["steps"], [value])

    def test_failure_keeps_previous_output_and_input(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source, output = folder / "bad.json", folder / "review.html"
            source.write_text("{}")
            output.write_text("previous")
            run = subprocess.run([sys.executable, str(ROOT / "scripts/render_review.py"), str(source), "--output", str(output)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(output.read_text(), "previous")
            run = subprocess.run([sys.executable, str(ROOT / "scripts/render_review.py"), str(source), "--output", str(source)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(source.read_text(), "{}")

    def test_cli_generation_uses_latest_template(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "review.html"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/render_review.py"), str(ROOT / "assets/example-review.json"), "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            original_js = (ROOT / "assets/swimlane-review.html").read_text().split("<script>")[1]
            self.assertEqual(out.read_text().split("<script>")[1], original_js)


if __name__ == "__main__":
    unittest.main()
