"""Check SKILL.md frontmatter version sync with plugin.json files.

Rules:
- Single-skill plugin (e.g. wechat-formatter): plugin.json version must match
  the only skill's SKILL.md frontmatter version.
- Multi-skill plugin (e.g. testing): plugin.json version must match the
  bundle/meta skill's version. The bundle skill is identified by having a
  name ending with "-bundle" or by being the only skill that references
  other skills (routing). If no bundle found, plugin version check is skipped.

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
