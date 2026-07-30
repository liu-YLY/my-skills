"""Check structural consistency invariants for every skill.

Guards against the recurring "silent doc drift" class that link/version/count
checks do not catch: files that no longer participate in the SKILL.md load
graph, module names referenced but never defined, and SKILL_ROOT export paths
that do not match the file's real repository location.

Three invariants are checked per skill:

1. Reachability (dead / unindexed markdown):
   Every ``*.md`` under a skill directory must be reachable from ``SKILL.md``
   by following relative markdown links (directory links expand to the files
   they contain). ``SKILL.md`` / ``README.md`` and the skill-level ``docs/``
   directory are human-facing meta docs, outside the load graph, and excluded.
   Only ``.md`` files are reported, so CSS / images / scripts never produce
   false positives.

2. Module definitions (ghost modules):
   For a skill that defines a ``:::module`` system (identified by
   ``layout/layout-modules.md``), every module name used in a ``:::name`` block
   or in a ``a + b + c`` recommended-combination expression must have a
   ``#### name —`` definition in ``layout-modules.md``.

3. SKILL_ROOT export path:
   Every ``export SKILL_ROOT=<path>`` line in ``integrations/quickstart.md``
   whose value starts with ``plugins/`` must equal the skill's real path
   relative to the repository root. Quickstarts without such a line are skipped
   (e.g. MCP-config quickstarts that carry no SKILL_ROOT).

Usage: python scripts/check-skill-consistency.py
Exit code: 0 if all invariants hold, 1 if any issue found.
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)')
SKIP_PREFIXES = ('http://', 'https://', 'mailto:')
# Meta markdown files that never participate in the SKILL.md load graph.
META_MD = ('SKILL.md', 'README.md', 'CHANGELOG.md')

MODULE_USE_RE = re.compile(r':::([a-z][a-z0-9-]*)')
# Generic syntax placeholders that are not real module names (e.g. the
# ":::module" token used when explaining the block syntax itself).
MODULE_USE_PLACEHOLDERS = {'module'}
MODULE_DEF_RE = re.compile(r'^####\s+([a-z][a-z0-9-]*)\s*[—-]', re.MULTILINE)
COMBO_TOKEN_RE = re.compile(r'^[a-z][a-z0-9-]*$')
EXPORT_SKILL_ROOT_RE = re.compile(r'export\s+SKILL_ROOT=([^\s`]+)')


def iter_skill_dirs(root: Path):
    for skill_dir in sorted(root.glob('plugins/*/skills/*/')):
        if skill_dir.is_dir():
            yield skill_dir


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def check_reachability(skill_dir: Path, root: Path) -> list[str]:
    """Every .md under the skill must be reachable from SKILL.md."""
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        return []

    reachable: set[Path] = {skill_md.resolve()}
    queue = [skill_md.resolve()]
    while queue:
        cur = queue.pop()
        if cur.suffix != '.md':
            continue
        for m in LINK_RE.finditer(_read(cur)):
            link = m.group(1)
            if link.startswith(SKIP_PREFIXES):
                continue
            if '/' not in link and '.' not in link:
                continue  # placeholder token in a syntax example
            target = (cur.parent / link).resolve()
            if target.is_dir():
                for f in target.rglob('*'):
                    if f.is_file() and f not in reachable:
                        reachable.add(f)
                        if f.suffix == '.md':
                            queue.append(f)
                continue
            if target.exists() and target not in reachable:
                reachable.add(target)
                queue.append(target)

    docs_dir = (skill_dir / 'docs').resolve()
    errors = []
    for md in sorted(skill_dir.rglob('*.md')):
        if '.venv-tools' in str(md):
            continue
        if md.name in META_MD:
            continue
        if docs_dir in md.resolve().parents:
            continue  # human-facing meta docs, outside the load graph
        if md.resolve() not in reachable:
            errors.append(
                f"{md.relative_to(root).as_posix()}: not reachable from "
                f"{skill_dir.name}/SKILL.md (dead / unindexed file)"
            )
    return errors


def check_module_definitions(skill_dir: Path, root: Path) -> list[str]:
    """Every used :::module / combination token must be defined."""
    layout = skill_dir / 'layout' / 'layout-modules.md'
    if not layout.exists():
        return []

    defined = set(MODULE_DEF_RE.findall(_read(layout)))
    used: dict[str, str] = {}  # module name -> first location seen

    for md in sorted(skill_dir.rglob('*.md')):
        if '.venv-tools' in str(md):
            continue
        rel = md.relative_to(root).as_posix()
        text = _read(md)
        for name in MODULE_USE_RE.findall(text):
            if name in MODULE_USE_PLACEHOLDERS:
                continue
            used.setdefault(name, rel)
        for line in text.splitlines():
            if ' + ' not in line:
                continue
            # Only treat as a module combination when every token qualifies.
            cell = line.split('|')[-2] if line.count('|') >= 2 else line
            tokens = [t.strip() for t in cell.split('+')]
            if len(tokens) >= 2 and all(COMBO_TOKEN_RE.match(t) for t in tokens):
                for t in tokens:
                    used.setdefault(t, rel)

    errors = []
    for name, rel in sorted(used.items()):
        if name not in defined:
            errors.append(
                f"{rel}: module '{name}' is referenced but not defined in "
                f"layout/layout-modules.md (ghost module)"
            )
    return errors


def check_skill_root(skill_dir: Path, root: Path) -> list[str]:
    """export SKILL_ROOT=plugins/... must match the skill's real path."""
    quickstart = skill_dir / 'integrations' / 'quickstart.md'
    if not quickstart.exists():
        return []

    expected = skill_dir.resolve().relative_to(root).as_posix()
    errors = []
    for m in EXPORT_SKILL_ROOT_RE.finditer(_read(quickstart)):
        value = m.group(1).rstrip('/')
        if not value.startswith('plugins/'):
            continue
        if value != expected:
            errors.append(
                f"{quickstart.relative_to(root).as_posix()}: "
                f"export SKILL_ROOT={value} != actual {expected}"
            )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = []

    for skill_dir in iter_skill_dirs(root):
        errors.extend(check_reachability(skill_dir, root))
        errors.extend(check_module_definitions(skill_dir, root))
        errors.extend(check_skill_root(skill_dir, root))

    if errors:
        print("Skill consistency issues found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All skill consistency invariants hold.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
