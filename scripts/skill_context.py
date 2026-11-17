"""Shared helpers for measuring skill default-path context budgets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

CONFIG_PATH = Path(__file__).resolve().parent / "context-budget.json"
FALLBACK_CHARS_PER_TOKEN = 1.55

_ENCODING = None
_ENCODING_TRIED = False


def load_config(path: Path = CONFIG_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("skills"), dict):
        raise ValueError(f"{path}: expected a 'skills' object")
    return data


def skill_dir(root: Path, skill: str) -> Path:
    matches = sorted(root.glob(f"plugins/*/skills/{skill}"))
    if not matches:
        raise FileNotFoundError(f"{root}: skill directory not found: {skill}")
    if len(matches) > 1:
        raise ValueError(f"{root}: duplicate skill directory: {skill}")
    return matches[0]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def measure_files(root: Path, skill: str, files: Iterable[str]) -> dict:
    base = skill_dir(root, skill)
    chars = lines = size = 0
    measured = []
    missing = []
    for rel in files:
        path = base / rel
        if not path.exists():
            missing.append(rel)
            continue
        text = read_text(path)
        chars += len(text)
        lines += text.count("\n") + 1
        size += len(text.encode("utf-8"))
        measured.append({"path": rel, "characters": len(text), "lines": text.count("\n") + 1})
    return {
        "characters": chars,
        "lines": lines,
        "bytes": size,
        "files": measured,
        "missing": missing,
    }


def all_markdown_characters(root: Path, skill: str) -> int:
    base = skill_dir(root, skill)
    return sum(len(read_text(path)) for path in base.rglob("*.md"))


def count_tokens(text: str) -> int | None:
    """Return o200k_base token count when tiktoken is available."""
    global _ENCODING, _ENCODING_TRIED
    if not _ENCODING_TRIED:
        _ENCODING_TRIED = True
        try:
            import tiktoken

            _ENCODING = tiktoken.get_encoding("o200k_base")
        except Exception:
            _ENCODING = None
    if _ENCODING is None:
        return None
    return len(_ENCODING.encode(text))


def measure_mode(root: Path, skill: str, mode: dict) -> dict:
    measured = measure_files(root, skill, mode.get("files", []))
    base = skill_dir(root, skill)
    token_total = 0
    token_known = True
    for item in measured["files"]:
        count = count_tokens(read_text(base / item["path"]))
        if count is None:
            token_known = False
            break
        token_total += count
        item["tokens"] = count
    if token_known and measured["files"]:
        measured["tokens"] = token_total
        measured["token_method"] = "tiktoken:o200k_base"
    else:
        measured["tokens"] = round(measured["characters"] / FALLBACK_CHARS_PER_TOKEN)
        measured["token_method"] = "fallback:characters/1.55"
    measured["mode"] = mode.get("description", "")
    measured["budget"] = mode.get("budget")
    measured["target"] = mode.get("target")
    return measured


def measure_skill(root: Path, skill: str, config: dict) -> dict:
    skill_config = config["skills"][skill]
    modes = {}
    covered = set()
    for name, mode in skill_config.get("modes", {}).items():
        measured = measure_mode(root, skill, mode)
        modes[name] = measured
        covered.update(item["path"] for item in measured["files"])
    total = all_markdown_characters(root, skill)
    covered_chars = sum(measured["characters"] for measured in modes.values())
    return {
        "skill": skill,
        "modes": modes,
        "total_markdown_characters": total,
        "other_markdown_characters": max(0, total - covered_chars),
        "covered_files": sorted(covered),
    }


def measure_all(root: Path, config: dict, skill: str | None = None) -> dict:
    names = [skill] if skill else sorted(config["skills"])
    return {
        "root": str(root),
        "unit": config.get("unit", "characters"),
        "skills": {name: measure_skill(root, name, config) for name in names},
    }
