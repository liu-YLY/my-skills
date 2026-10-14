from pathlib import Path

import re
import shlex
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_quick_start_installs_every_testing_skill():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "for skill_dir in plugins/testing/skills/*" in readme
    assert "cp -r plugins/testing/skills/testing-bundle" not in readme


def test_documented_converter_dependency_path_exists():
    guide = (ROOT / "docs/installation.md").read_text(encoding="utf-8")
    relative_path = "plugins/testing/skills/test-case-engineer/scripts"
    assert f"cd {relative_path}" in guide
    assert (ROOT / relative_path / "requirements.txt").is_file()
    assert not (ROOT / "plugins/testing/scripts").exists()


@pytest.mark.parametrize("mode", ["当前改动", "暂存区改动", "分支对比", "单个 Commit", "Commit 范围", "Revision Range"])
def test_documented_diff_modes_do_not_execute_textconv(tmp_path, mode):
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True,
                              capture_output=True, text=True).stdout

    git("init", "-q", "-b", "main")
    git("config", "user.name", "Skill fixture")
    git("config", "user.email", "fixture@example.invalid")
    (tmp_path / ".gitattributes").write_text("*.txt diff=fixture\n")
    source = tmp_path / "sample.txt"
    source.write_text("baseline\n")
    git("add", ".")
    git("commit", "-qm", "fixture baseline")
    git("checkout", "-qb", "feature")
    source.write_text("committed\n")
    git("add", "sample.txt")
    git("commit", "-qm", "fixture change")
    source.write_text("staged\n")
    git("add", "sample.txt")
    marker = tmp_path / "textconv-called"
    converter = tmp_path / "converter.py"
    converter.write_text("from pathlib import Path\nimport sys\n"
                         f"Path({str(marker)!r}).write_text('called')\n"
                         "print(Path(sys.argv[1]).read_text())\n")
    git("config", "diff.fixture.textconv", shlex.join([sys.executable, str(converter)]))
    guide = ROOT / "plugins/testing/skills/change-impact-analyzer/knowledge/diff-modes.md"
    row = next(line for line in guide.read_text().splitlines() if line.startswith(f"| {mode} |"))
    commands = re.findall(r"`(git diff [^`]+)`", row)
    assert commands
    refs = {"<default>": "main", "<base>": "main", "<head>": "HEAD",
            "<commit>": "HEAD", "<commit1>": "HEAD~1", "<commit2>": "HEAD",
            "<range>": "main..HEAD"}
    for command in commands:
        for placeholder, value in refs.items():
            command = command.replace(placeholder, value)
        output = git(*shlex.split(command)[1:])
        assert not marker.exists(), f"documented command executed textconv: {command}"
        assert "+committed" in output or "+staged" in output


def test_documented_root_commit_diff_preserves_first_commit_content(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args],
                              cwd=tmp_path, check=True, capture_output=True,
                              text=True).stdout

    git("init", "-q", "-b", "develop")
    (tmp_path / "policy.py").write_text("LIMIT = 20\n")
    git("add", "policy.py")
    git("-c", "user.name=Skill fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "initial policy")
    guide = ROOT / "plugins/testing/skills/change-impact-analyzer/knowledge/diff-modes.md"
    command = re.search(r"`(git show --root [^`]+)`", guide.read_text()).group(1)
    before = git("status", "--porcelain")
    output = git(*shlex.split(command.replace("<commit>", "HEAD"))[1:])
    assert "+LIMIT = 20" in output
    assert "diff --git a/policy.py b/policy.py" in output
    assert git("status", "--porcelain") == before
