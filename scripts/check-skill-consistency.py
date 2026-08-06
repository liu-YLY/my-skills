"""Check structural consistency invariants for every skill.

Guards against the recurring "silent doc drift" class that link/version/count
checks do not catch: files that no longer participate in the SKILL.md load
graph, module names referenced but never defined, and SKILL_ROOT export paths
that do not match the file's real repository location.

Six invariants are checked per skill:

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

4. Mode definition consistency:
   If ``test-case-engineer-core.md`` (or any ``*-core.md``) defines a
   ``## 模式切换`` section with ``- **{mode}**:`` entries, the mode names must
   be consistent with every ``模式切换`` / ``模式`` reference in ``SKILL.md``
   and the mode table in ``README.md``.  Catches the class of bug where a new
   mode is added to core.md but SKILL.md still says "四种模式" or omits the
   new mode from the read-matrix.

5. Security constraint coverage:
   If the skill executes shell commands (``markitdown``, ``convert_docs``,
   ``git diff``, ``exec``, ``subprocess``, ``pandoc``) in knowledge/ or
   integrations/ files, then ``integrations/quickstart.md`` must contain a
   ``## 安全约束`` section AND every file that contains a shell execution point
   must either contain a ``安全提示`` / ``安全约束`` reference itself or be
   reachable from quickstart.md via a relative link.

6. Core file line count:
   Every ``*-core.md`` file must be ≤ 500 lines (Anthropic Skills best
   practice).  Exceeding the threshold triggers an error prompting the author
   to split content into knowledge/ files.

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

# --- Mode consistency (invariant 4) ---
# Matches mode definitions in core.md: "- **默认**：" / "- **回归验证清单**："
MODE_DEF_RE = re.compile(r'^- \*\*(.+?)\*\*[：:]', re.MULTILINE)
# Matches mode-list summaries in SKILL.md/README.md: "默认/快速/探索式/评审"
MODE_LIST_RE = re.compile(r'模式[切换]?[：:]\s*(.+?)(?:五种|四种|三种|两种|\d+种)?模式', re.MULTILINE)
# Matches the mode count word: "四种模式" / "五种模式"
MODE_COUNT_RE = re.compile(r'(四种|五种|三种|两种|\d+)种模式')
# Known mode synonyms that refer to the same concept (maps variants to canonical name)
MODE_SYNONYMS = {
    '回归验证清单': '回归验证清单',
    '回归验证': '回归验证清单',
}

# --- Security constraint coverage (invariant 5) ---
# Shell command patterns that indicate a shell execution point
SHELL_CMD_PATTERNS = [
    r'markitdown\b',
    r'convert_docs\b',
    r'git\s+diff\b',
    r'\bexec\b',
    r'\bsubprocess\b',
    r'\bpandoc\b',
]
SHELL_CMD_RE = re.compile('|'.join(SHELL_CMD_PATTERNS), re.IGNORECASE)
SECURITY_HEADING_RE = re.compile(r'^##\s+安全约束\b', re.MULTILINE)
SECURITY_REF_RE = re.compile(r'安全约束|安全提示', re.MULTILINE)
# Fenced code block: ``` ... ``` or ~~~ ... ~~~ (captures content incl. language tag)
FENCED_CODE_BLOCK_RE = re.compile(
    r'^(?:```|~~~)[^\n]*\n(.*?)^(?:```|~~~)\s*$',
    re.MULTILINE | re.DOTALL,
)
# Inline code: `...` (single backtick, not part of fenced block)
INLINE_CODE_RE = re.compile(r'`([^`\n]+)`')

# --- Core file line count (invariant 6) ---
CORE_LINE_LIMIT = 500


def iter_skill_dirs(root: Path):
    for skill_dir in sorted(root.glob('plugins/*/skills/*/')):
        if skill_dir.is_dir():
            yield skill_dir


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def _extract_code_segments(text: str) -> str:
    """Extract only code blocks and inline code from markdown text.

    This filters out plain-text descriptions of commands (e.g. "git diff" in
    a flowchart or paragraph) so that only actual command references inside
    backticks or fenced code blocks are checked for shell execution points.

    Within fenced code blocks, lines containing CJK characters are excluded
    since real shell commands do not contain CJK text — this filters out
    ASCII-art flowcharts that happen to be wrapped in code fences.
    """
    segments: list[str] = []

    # Collect fenced code block contents and mask them out of inline scan
    masked = text
    for m in FENCED_CODE_BLOCK_RE.finditer(text):
        block = m.group(1)
        # Filter out lines with CJK characters (flowcharts, not commands)
        for line in block.splitlines():
            if not re.search(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', line):
                segments.append(line)
        # Replace the entire fenced block (incl. markers) with placeholders
        masked = masked.replace(m.group(0), '\n' * m.group(0).count('\n'))

    # Collect inline code from the remaining text (fenced blocks removed)
    for m in INLINE_CODE_RE.finditer(masked):
        segments.append(m.group(1))

    return '\n'.join(segments)


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


def _normalize_mode(name: str) -> str:
    """Map mode name variants to their canonical form."""
    return MODE_SYNONYMS.get(name, name)


def _extract_core_modes(text: str) -> list[str]:
    """Extract mode names from a ``## 模式切换`` section in core.md.

    Looks for ``- **{mode}**:`` entries only within the section bounded by
    ``## 模式切换`` and the next ``---`` or ``## `` heading.
    """
    # Find the 模式切换 section
    section_start = text.find('## 模式切换')
    if section_start == -1:
        return []
    # Section ends at the next horizontal rule or level-2 heading
    rest = text[section_start:]
    # Find the next '---' or '## ' after the section heading itself
    lines = rest.splitlines()
    section_lines = []
    found_heading = False
    for line in lines:
        if not found_heading:
            if line.startswith('## 模式切换'):
                found_heading = True
            continue
        if line.startswith('---') or (line.startswith('## ') and not line.startswith('### ')):
            break
        section_lines.append(line)
    section_text = '\n'.join(section_lines)
    return [m.strip() for m in MODE_DEF_RE.findall(section_text)]


def _extract_mode_list_from_line(text: str) -> set[str] | None:
    """Extract mode names from a slash-separated list like '默认/快速/探索式/评审'.

    Returns None if the text doesn't contain a recognizable mode list.
    Only processes slash-separated lists preceded by '模式' keyword to avoid
    false positives from table cells and other slash-usage.
    """
    matches = []
    # Match patterns like "模式切换：默认/快速/回归验证清单/探索式/评审 五种模式"
    for m in re.finditer(r'模式[切换]?\s*[：:]\s*(.+?)(?:\s+(?:五种|四种|三种|两种|\d+种)模式|。|$)', text, re.MULTILINE):
        raw = m.group(1).strip()
        # Only process if it looks like a slash-separated list
        if '/' in raw:
            parts = [p.strip() for p in raw.split('/') if p.strip()]
            # Filter out non-mode tokens: mode names are short (≤10 chars),
            # contain no parentheses, no spaces, no markdown links
            parts = [p for p in parts
                     if not p.startswith('http')
                     and not p.startswith('[')
                     and len(p) <= 10
                     and '（' not in p and '(' not in p
                     and '）' not in p and ')' not in p]
            # Strip trailing '模式' suffix (e.g. '探索式模式' -> '探索式')
            parts = [re.sub(r'模式$', '', p) for p in parts]
            parts = [p for p in parts if p]
            if parts:
                matches.append(parts)

    if not matches:
        return None
    result: set[str] = set()
    for parts in matches:
        for p in parts:
            result.add(_normalize_mode(p))
    return result


def check_mode_consistency(skill_dir: Path, root: Path) -> list[str]:
    """Mode names in core.md must match references in SKILL.md and README.md."""
    # Find core.md file (test-case-engineer-core.md, etc.)
    core_files = list(skill_dir.glob('*-core.md'))
    if not core_files:
        return []
    core_file = core_files[0]
    core_text = _read(core_file)

    # Extract canonical mode set from core.md
    core_modes_raw = _extract_core_modes(core_text)
    if not core_modes_raw:
        return []
    core_modes = {_normalize_mode(m) for m in core_modes_raw}

    errors = []
    core_rel = core_file.relative_to(root).as_posix()

    # Check SKILL.md
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        skill_text = _read(skill_md)
        skill_rel = skill_md.relative_to(root).as_posix()

        # Check mode count claims: "四种模式" should match actual count
        for m in MODE_COUNT_RE.finditer(skill_text):
            count_word = m.group(1)
            count_map = {'四种': 4, '五种': 5, '三种': 3, '两种': 2}
            claimed = count_map.get(count_word, int(count_word) if count_word.isdigit() else None)
            if claimed is not None and claimed != len(core_modes):
                errors.append(
                    f"{skill_rel}: claims '{count_word}模式' but core.md defines "
                    f"{len(core_modes)} modes: {sorted(core_modes)}"
                )

        # Check that every core mode appears somewhere in SKILL.md
        for mode in sorted(core_modes):
            if mode not in skill_text:
                errors.append(
                    f"{skill_rel}: mode '{mode}' is defined in {core_rel} "
                    f"but not mentioned in SKILL.md"
                )

        # Check that modes in SKILL.md mode-list references are subset of core modes
        skill_mode_list = _extract_mode_list_from_line(skill_text)
        if skill_mode_list:
            extra = skill_mode_list - core_modes
            if extra:
                errors.append(
                    f"{skill_rel}: references modes {sorted(extra)} not defined "
                    f"in {core_rel} (defined: {sorted(core_modes)})"
                )

    # Check README.md
    readme = skill_dir / 'README.md'
    if readme.exists():
        readme_text = _read(readme)
        readme_rel = readme.relative_to(root).as_posix()

        for mode in sorted(core_modes):
            if mode not in readme_text:
                errors.append(
                    f"{readme_rel}: mode '{mode}' is defined in {core_rel} "
                    f"but not mentioned in README.md"
                )

    return errors


def check_security_coverage(skill_dir: Path, root: Path) -> list[str]:
    """Shell execution points must be covered by security constraints."""
    quickstart = skill_dir / 'integrations' / 'quickstart.md'

    # Find all .md files under knowledge/ and integrations/ that contain shell commands
    shell_files: list[tuple[Path, str]] = []
    for sub in ('knowledge', 'integrations'):
        search_dir = skill_dir / sub
        if not search_dir.is_dir():
            continue
        for md in sorted(search_dir.rglob('*.md')):
            if '.venv-tools' in str(md):
                continue
            text = _read(md)
            code_text = _extract_code_segments(text)
            if SHELL_CMD_RE.search(code_text):
                shell_files.append((md, text))

    if not shell_files:
        return []

    errors = []

    # Check that quickstart.md has a 安全约束 section
    has_security_section = False
    quickstart_text = ''
    if quickstart.exists():
        quickstart_text = _read(quickstart)
        has_security_section = bool(SECURITY_HEADING_RE.search(quickstart_text))

    if not has_security_section:
        errors.append(
            f"{quickstart.relative_to(root).as_posix()}: missing '## 安全约束' "
            f"section (shell commands found in {len(shell_files)} file(s))"
        )

    # Check that each file with shell commands has a 安全提示/安全约束 reference
    for md, text in shell_files:
        if not SECURITY_REF_RE.search(text):
            rel = md.relative_to(root).as_posix()
            errors.append(
                f"{rel}: contains shell execution points but has no "
                f"'安全提示' or '安全约束' reference"
            )

    return errors


def check_core_line_count(skill_dir: Path, root: Path) -> list[str]:
    """Core files (*-core.md) must not exceed 500 lines."""
    errors = []
    for core_file in sorted(skill_dir.glob('*-core.md')):
        line_count = len(_read(core_file).splitlines())
        if line_count > CORE_LINE_LIMIT:
            rel = core_file.relative_to(root).as_posix()
            errors.append(
                f"{rel}: {line_count} lines exceeds {CORE_LINE_LIMIT}-line limit "
                f"(split content into knowledge/ files)"
            )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = []

    for skill_dir in iter_skill_dirs(root):
        errors.extend(check_reachability(skill_dir, root))
        errors.extend(check_module_definitions(skill_dir, root))
        errors.extend(check_skill_root(skill_dir, root))
        errors.extend(check_mode_consistency(skill_dir, root))
        errors.extend(check_security_coverage(skill_dir, root))
        errors.extend(check_core_line_count(skill_dir, root))

    if errors:
        print("Skill consistency issues found:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All skill consistency invariants hold.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
