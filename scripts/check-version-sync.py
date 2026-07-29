"""Check SKILL.md frontmatter version sync with plugin.json files.

Rules:
- Single-skill plugin (e.g. wechat-formatter): plugin.json version must match
  the only skill's SKILL.md frontmatter version.
- Multi-skill plugin (e.g. testing): plugin.json version must match the
  bundle/meta skill's version. The bundle skill is identified by having a
  name ending with "-bundle" or by being the only skill that references
  other skills (routing). If no bundle found, plugin version check is skipped.
- Bundle skill content consistency: CHANGELOG.md must have a [X.Y.Z] entry
  matching the current frontmatter version; architecture diagram version
  labels in SKILL.md must match frontmatter; test-prompts.json expected
  fields must not carry historical "vX.Y.Z " version prefixes.

Usage: python scripts/check-version-sync.py
Exit code: 0 if all versions in sync, 1 if any mismatch found.
"""
import json
import re
import sys
from pathlib import Path


def extract_skill_version(skill_md: Path) -> str | None:
    """Extract version from SKILL.md frontmatter."""
    if not skill_md.exists():
        return None
    content = skill_md.read_text(encoding='utf-8')
    m = re.search(r'^version:\s*"?([\d.]+)"?', content, re.MULTILINE)
    return m.group(1) if m else None


def find_bundle_skill(skills_dir: Path) -> Path | None:
    """Find the bundle/meta skill in a multi-skill plugin.

    Heuristic: skill name ends with '-bundle' or 'testing-bundle'.
    """
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name.endswith('-bundle'):
            return skill_dir
    return None


def check_changelog_has_version(skill_dir: Path, version: str) -> str | None:
    """Check that CHANGELOG.md has an entry for the current version.

    Returns error message if CHANGELOG exists but lacks a [X.Y.Z] header
    matching the current frontmatter version.
    """
    changelog = skill_dir / 'CHANGELOG.md'
    if not changelog.exists():
        return None  # No CHANGELOG is acceptable (not all skills have one)
    content = changelog.read_text(encoding='utf-8')
    pattern = rf'^##\s*\[{re.escape(version)}\]'
    if not re.search(pattern, content, re.MULTILINE):
        return (
            f"{changelog}: missing '## [{version}]' entry for current version"
        )
    return None


def check_skill_diagram_version(skill_md: Path, version: str, skill_name: str) -> str | None:
    """Check that architecture diagram version labels match frontmatter.

    Looks for "{skill_name} vX.Y.Z" patterns (e.g. in ASCII architecture
    diagrams) and verifies they match the frontmatter version.
    """
    content = skill_md.read_text(encoding='utf-8')
    diagram_pattern = rf'{re.escape(skill_name)}\s+v(\d+\.\d+\.\d+)'
    mismatches = []
    for m in re.finditer(diagram_pattern, content):
        found_version = m.group(1)
        if found_version != version:
            mismatches.append(found_version)
    if mismatches:
        unique = sorted(set(mismatches))
        return (
            f"{skill_md}: architecture diagram references v{unique[0]} "
            f"but frontmatter version is {version}"
        )
    return None


def check_test_prompts_version_drift(skill_dir: Path) -> list[str]:
    """Check that test-prompts.json expected fields lack version-prefix drift.

    Flags expected fields starting with "vX.Y.Z " — historical version markers
    that create drift when the current version changes.
    """
    errors = []
    test_prompts = skill_dir / 'test-prompts.json'
    if not test_prompts.exists():
        return errors
    try:
        prompts = json.loads(test_prompts.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return errors  # JSON validity is checked by other tooling
    for prompt in prompts:
        expected = prompt.get('expected', '')
        if re.match(r'^v\d+\.\d+\.\d+\s', expected):
            errors.append(
                f"{test_prompts}: prompt id {prompt.get('id', '?')} expected "
                f"field has version prefix — remove historical version markers"
            )
    return errors


def check_plugin_readme_version(plugin_root: Path, expected_version: str) -> str | None:
    """Check that plugin root README.md does not carry a stale version string.

    Looks for "当前版本：vX.Y.Z" patterns (Chinese, allows markdown bold/italic
    markers between the label and colon) and verifies the version matches
    `expected_version`. Returns error message on mismatch.
    """
    readme = plugin_root / 'README.md'
    if not readme.exists():
        return None
    content = readme.read_text(encoding='utf-8')
    pattern = r'当前版本[*_]*[：:]\s*v?(\d+\.\d+\.\d+)'
    m = re.search(pattern, content)
    if m and m.group(1) != expected_version:
        return (
            f"{readme}: '当前版本' references v{m.group(1)} but "
            f"plugin manifest version is {expected_version}"
        )
    return None


def check_plugin_readme_skill_versions(plugin_root: Path, skills_dir: Path) -> list[str]:
    """Check that plugin root README.md architecture diagram and capability
    matrix versions match each skill's SKILL.md frontmatter version.

    Scans for "{skill_name} v{X.Y.Z}" patterns in README.md and compares
    against the frontmatter version of the corresponding skill.
    """
    errors = []
    readme = plugin_root / 'README.md'
    if not readme.exists():
        return errors
    content = readme.read_text(encoding='utf-8')

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_name = skill_dir.name
        skill_md = skill_dir / 'SKILL.md'
        expected = extract_skill_version(skill_md)
        if not expected:
            continue
        # Match "skill-name vX.Y.Z" in README (architecture diagram, capability matrix)
        pattern = rf'{re.escape(skill_name)}\s+v(\d+\.\d+\.\d+)'
        for m in re.finditer(pattern, content):
            found = m.group(1)
            if found != expected:
                errors.append(
                    f"{readme}: references '{skill_name} v{found}' but "
                    f"SKILL.md frontmatter version is {expected}"
                )
    return errors


def check_plugin(plugin_root: Path) -> list[str]:
    """Check version sync for a single plugin.

    Returns list of error messages (empty if all OK).
    """
    errors = []
    skills_dir = plugin_root / 'skills'
    if not skills_dir.exists():
        return errors

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]

    for runtime_dir in ('.claude-plugin', '.cursor-plugin', '.codex-plugin'):
        plugin_json = plugin_root / runtime_dir / 'plugin.json'
        if not plugin_json.exists():
            continue

        try:
            data = json.loads(plugin_json.read_text(encoding='utf-8'))
            plugin_version = data.get('version', '')
        except json.JSONDecodeError as e:
            errors.append(f"{plugin_json}: invalid JSON - {e}")
            continue

        if not plugin_version:
            continue

        # Plugin root README.md "当前版本" must match manifest version
        err = check_plugin_readme_version(plugin_root, plugin_version)
        if err:
            errors.append(err)

        if len(skill_dirs) == 1:
            # Single-skill plugin: plugin.json version must match SKILL.md version
            skill_md = skill_dirs[0] / 'SKILL.md'
            skill_version = extract_skill_version(skill_md)
            if skill_version and skill_version != plugin_version:
                errors.append(
                    f"{plugin_json}: version {plugin_version} != "
                    f"{skill_md.name} {skill_version} (single-skill plugin)"
                )
        else:
            # Multi-skill plugin: plugin.json version must match bundle skill version
            bundle_dir = find_bundle_skill(skills_dir)
            if bundle_dir:
                bundle_md = bundle_dir / 'SKILL.md'
                bundle_version = extract_skill_version(bundle_md)
                if bundle_version and bundle_version != plugin_version:
                    errors.append(
                        f"{plugin_json}: version {plugin_version} != "
                        f"bundle {bundle_md.name} {bundle_version} (multi-skill plugin)"
                    )
            # If no bundle found, skip plugin version check (cannot determine expected version)

    # Content consistency checks for bundle skill (CHANGELOG, diagram, test-prompts)
    bundle_dir = find_bundle_skill(skills_dir)
    if bundle_dir:
        bundle_md = bundle_dir / 'SKILL.md'
        bundle_version = extract_skill_version(bundle_md)
        if bundle_version:
            # CHANGELOG must have current version entry
            err = check_changelog_has_version(bundle_dir, bundle_version)
            if err:
                errors.append(err)
            # Architecture diagram version must match frontmatter
            err = check_skill_diagram_version(bundle_md, bundle_version, bundle_dir.name)
            if err:
                errors.append(err)
            # test-prompts must not have historical version prefixes
            errors.extend(check_test_prompts_version_drift(bundle_dir))

    # Plugin root README.md skill version references (architecture diagram, capability matrix)
    errors.extend(check_plugin_readme_skill_versions(plugin_root, skills_dir))

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    plugins_dir = root / 'plugins'
    errors = []

    for plugin_root in plugins_dir.iterdir():
        if not plugin_root.is_dir():
            continue
        errors.extend(check_plugin(plugin_root))

    if errors:
        print("Version sync issues found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("All version numbers are in sync.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
