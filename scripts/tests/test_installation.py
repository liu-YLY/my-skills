import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def powershell():
    executable = os.environ.get("SKILL_TEST_PWSH") or shutil.which("pwsh")
    if not executable:
        if os.environ.get("CI"):
            pytest.fail("PowerShell is required for the CI installer smoke test")
        pytest.skip("PowerShell unavailable; CI runs this installer smoke test")
    return executable


def test_installer_delivers_all_skills_and_preserves_other_directories(tmp_path):
    executable = powershell()
    target = tmp_path / "runtime skills"
    unrelated = target / "user-other-skill/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("user-owned")
    command = [executable, "-NoLogo", "-NoProfile", "-File",
               str(ROOT / "scripts/install-testing-bundle.ps1"), "-TargetDir", str(target)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    installed = {p.parent.name for p in target.glob("*/SKILL.md")} - {"user-other-skill"}
    expected = {p.parent.name for p in (ROOT / "plugins/testing/skills").glob("*/SKILL.md")}
    assert installed == expected and len(installed) == 7
    for name in ("convert_docs.py", "requirements.txt"):
        assert (target / "test-case-engineer/scripts" / name).is_file()
    subprocess.run(command + ["-Uninstall"], check=True, capture_output=True, text=True)
    assert list(target.glob("*/SKILL.md")) == [unrelated]
    assert unrelated.read_text() == "user-owned"


def test_installer_validates_resources_before_changing_target(tmp_path):
    executable = powershell()
    source = tmp_path / "source"
    (source / "scripts").mkdir(parents=True)
    installer = source / "scripts/install-testing-bundle.ps1"
    shutil.copyfile(ROOT / "scripts/install-testing-bundle.ps1", installer)
    for skill in ("testing-bundle", "test-case-engineer", "bug-analyzer"):
        folder = source / "plugins/testing/skills" / skill
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text("test source")
    target = tmp_path / "target"
    target.mkdir()
    sentinel = target / "existing.txt"
    sentinel.write_text("unchanged")
    result = subprocess.run([executable, "-NoLogo", "-NoProfile", "-File", str(installer),
                             "-TargetDir", str(target)], capture_output=True, text=True)
    assert result.returncode != 0
    assert list(target.iterdir()) == [sentinel]
    assert sentinel.read_text() == "unchanged"


def test_installer_rejects_a_missing_referenced_skill(tmp_path):
    executable = powershell()
    source = tmp_path / "source"
    shutil.copytree(ROOT / "plugins/testing/skills", source / "plugins/testing/skills")
    (source / "scripts").mkdir()
    installer = source / "scripts/install-testing-bundle.ps1"
    shutil.copyfile(ROOT / "scripts/install-testing-bundle.ps1", installer)
    (source / "plugins/testing/skills/change-impact-analyzer/SKILL.md").unlink()
    target = tmp_path / "target"
    result = subprocess.run([executable, "-NoLogo", "-NoProfile", "-File", str(installer),
                             "-TargetDir", str(target)], capture_output=True, text=True)
    assert result.returncode != 0
    assert not target.exists()
