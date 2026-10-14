"""Check knowledge reference integrity for skills.

Replaces the former knowledge-file-count heuristic (which incentivised
padding knowledge/ with filler files). Verifies two invariants per skill:

1. Every relative file link in a skill's markdown files resolves to an
   existing file (referenced-file integrity).
2. Every knowledge/*.md file is referenced by at least one markdown file
   within the same skill (no orphan knowledge files).

Usage: python scripts/check-knowledge-count.py
Exit code: 0 if all references are intact, 1 if any issue found.
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)')
SKIP_PREFIXES = ('http://', 'https://', 'mailto:')


def iter_skill_dirs(root: Path):
    for skill_dir in sorted(root.glob('plugins/*/skills/*/')):
        if skill_dir.is_dir():
            yield skill_dir


def collect_md_files(skill_dir: Path) -> list[Path]:
    return [p for p in skill_dir.rglob('*.md') if '.venv-tools' not in str(p)]


def check_referenced_files(md_files: list[Path], root: Path) -> list[str]:
    """Every relative link target in the skill's markdown must exist.

    Targets without a path separator or file extension (e.g. ``url``,
    ``链接``, ``placeholder-url``) are treated as documentation placeholders
    inside syntax examples and skipped.
    """
    errors = []
    for md in md_files:
        text = md.read_text(encoding='utf-8', errors='replace')
        for m in LINK_RE.finditer(text):
            link = m.group(1)
            if link.startswith(SKIP_PREFIXES):
                continue
            if '/' not in link and '.' not in link:
                continue  # placeholder token in a syntax example, not a path
            target = (md.parent / link).resolve()
            if not target.exists():
                errors.append(f"{md.relative_to(root)} -> {link} (missing target)")
    return errors


def check_orphan_knowledge(skill_dir: Path, md_files: list[Path], root: Path) -> list[str]:
    """Every knowledge/*.md must be referenced by some markdown in the skill."""
    errors = []
    knowledge_dir = skill_dir / 'knowledge'
    if not knowledge_dir.exists():
        return errors
    pool = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in md_files)
    for kf in sorted(knowledge_dir.glob('*.md')):
        if kf.name not in pool:
            errors.append(
                f"{kf.relative_to(root)}: orphan knowledge file "
                f"(not referenced by any markdown in {skill_dir.name})"
            )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = []

    for skill_dir in iter_skill_dirs(root):
        md_files = collect_md_files(skill_dir)
        errors.extend(check_referenced_files(md_files, root))
        errors.extend(check_orphan_knowledge(skill_dir, md_files, root))

    if errors:
        print("Knowledge reference integrity issues found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All skill knowledge references are intact.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
