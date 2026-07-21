"""Check knowledge file count for non-meta skills.

Usage: python scripts/check-knowledge-count.py
Exit code: always 0 (warnings only, some skills have design exemptions).
"""
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    # testing-bundle is a meta skill, exempted
    exempted = {'testing-bundle'}
    skills = list(root.glob('plugins/*/skills/*/'))
    warnings = []

    for skill_dir in skills:
        skill_name = skill_dir.name
        if skill_name in exempted:
            continue

        knowledge_dir = skill_dir / 'knowledge'
        if not knowledge_dir.exists():
            warnings.append(f"{skill_dir}: knowledge/ directory missing")
            continue

        md_files = list(knowledge_dir.glob('*.md'))
        if len(md_files) < 4:
            warnings.append(
                f"{skill_dir}: knowledge/ has only {len(md_files)} .md files (expected >=4)"
            )

    if warnings:
        print("Knowledge file count warnings:")
        for w in warnings:
            print(f"  - {w}")
        print("\nNote: These are warnings, not failures. Some skills may have design exemptions.")
    else:
        print("All non-meta skills have >=4 knowledge files.")

    return 0  # warnings only, never fail


if __name__ == '__main__':
    sys.exit(main())
