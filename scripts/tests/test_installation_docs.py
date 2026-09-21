from pathlib import Path


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
