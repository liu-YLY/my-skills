"""Check relative markdown link integrity across the whole repository.

Guards against the P0 broken-link class: a SKILL.md / README / doc that
links to a relative file which does not exist. Complements
check-knowledge-count.py (skill-scoped) by covering top-level docs, CLAUDE.md,
CONTRIBUTING.md and every plugin/doc markdown file.

Scope rules:
- Only relative links are checked; http(s)/mailto are skipped.
- Targets without a path separator or file extension (e.g. ``url``, ``链接``)
  are documentation placeholders inside syntax examples and are skipped.
- ``docs/superpowers/`` is excluded: those are historical plan/design
  snapshots that intentionally reference not-yet-created files.

Usage: python scripts/check-md-links.py
Exit code: 0 if all relative links resolve, 1 if any broken link found.
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)')
SKIP_PREFIXES = ('http://', 'https://', 'mailto:')
EXCLUDE_DIR_PARTS = ('.git', '.venv-tools', 'node_modules')
# Historical plan/design snapshots referencing not-yet-created files.
EXCLUDE_REL_PREFIXES = ('docs/superpowers/',)


def is_excluded(path: Path, root: Path) -> bool:
    if any(part in EXCLUDE_DIR_PARTS for part in path.parts):
        return True
    rel = path.relative_to(root).as_posix()
    return rel.startswith(EXCLUDE_REL_PREFIXES)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    broken = []

    for md in sorted(root.rglob('*.md')):
        if is_excluded(md, root):
            continue
        text = md.read_text(encoding='utf-8', errors='replace')
        for m in LINK_RE.finditer(text):
            link = m.group(1)
            if link.startswith(SKIP_PREFIXES):
                continue
            if '/' not in link and '.' not in link:
                continue  # placeholder token in a syntax example
            target = (md.parent / link).resolve()
            if not target.exists():
                broken.append(f"{md.relative_to(root).as_posix()} -> {link}")

    if broken:
        print("Broken relative markdown links found:")
        for b in broken:
            print(f"  - {b}")
        return 1
    print("All relative markdown links resolve.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
