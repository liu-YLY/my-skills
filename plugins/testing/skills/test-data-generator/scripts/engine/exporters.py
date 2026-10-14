import csv
import hashlib
import io
import json
from itertools import chain
from pathlib import Path

from .common import ResourceError, canonical, digest, strict_json
from .generators import schedule


def encode_csv(value):
    if value is None:
        return "\\N"
    if isinstance(value, str):
        return value.replace("\\", "\\\\")
    return canonical(value)


def decode_csv(value, field):
    if value == "\\N":
        return None
    if field["type"] in ("string", "decimal", "datetime"):
        result = []
        index = 0
        while index < len(value):
            if value[index] == "\\":
                if index + 1 >= len(value) or value[index + 1] != "\\":
                    raise ValueError("invalid CSV backslash escape")
                index += 1
            result.append(value[index])
            index += 1
        return "".join(result)
    try:
        return strict_json(value)
    except json.JSONDecodeError:
        return value


class Writer:
    def __init__(self, root, budget):
        self.root = Path(root)
        self.budget = budget
        self.bytes_written = 0
        self.files = {}

    def write(self, relative, chunks):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        checksum = hashlib.sha256()
        size = 0
        with path.open("xb") as handle:
            for chunk in chunks:
                self.budget.check()
                encoded = chunk.encode("utf-8")
                if self.bytes_written + len(encoded) > self.budget.limits["max_output_bytes"]:
                    raise ResourceError("output byte limit exceeded")
                handle.write(encoded)
                checksum.update(encoded)
                size += len(encoded)
                self.bytes_written += len(encoded)
        self.files[relative] = {"sha256": checksum.hexdigest(), "bytes": size}

    def json(self, relative, value):
        encoder = json.JSONEncoder(ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        self.write(relative, chain(encoder.iterencode(value), ["\n"]))


def csv_chunks(rows, fields):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(fields)
    yield buffer.getvalue()
    for row in rows:
        buffer.seek(0)
        buffer.truncate()
        writer.writerow([encode_csv(row[name]) for name in fields])
        yield buffer.getvalue()


def export_data(writer, profile, data, cases):
    entity_files = {}
    for entity in sorted(data):
        rows = data[entity]
        entity_files[entity] = {}
        for kind in profile["generation"]["output_formats"]:
            relative = f"data/{entity}.{kind}"
            if kind == "json":
                writer.json(relative, rows)
            elif kind == "jsonl":
                writer.write(relative, (canonical(row) + "\n" for row in rows))
            else:
                writer.write(relative, csv_chunks(rows, sorted(profile["entities"][entity]["fields"])))
            entity_files[entity][kind] = relative
    writer.write("negative/cases.jsonl", (canonical(case) + "\n" for case in cases))
    return entity_files


def checked_path(root, relative):
    if not isinstance(relative, str):
        raise ValueError("dataset paths must be strings")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("dataset path escapes its directory")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("dataset symlink escapes its directory")
    return resolved


def read_rows(path, kind, fields):
    with path.open(encoding="utf-8", newline="") as handle:
        if kind == "json":
            rows = strict_json(handle.read())
        elif kind == "jsonl":
            rows = [strict_json(line) for line in handle if line.strip()]
        else:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("missing or duplicate CSV headers")
            rows = []
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("CSV row does not match its headers")
                rows.append({name: decode_csv(value, fields[name]) if name in fields else value for name, value in row.items()})
    if not isinstance(rows, list):
        raise ValueError("entity data must be an array")
    return rows


def read_bundle(profile, directory, budget):
    root = Path(directory).resolve()
    manifest_path = checked_path(root, "manifest.json")
    if manifest_path.is_file() and manifest_path.stat().st_size > min(4194304, budget.limits["max_output_bytes"]):
        raise ResourceError("manifest byte limit exceeded")
    manifest = strict_json(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else None
    issues = []
    total_bytes = 0
    measured = set()
    def measure(path):
        nonlocal total_bytes
        if path not in measured:
            measured.add(path)
            total_bytes += path.stat().st_size
            if total_bytes > budget.limits["max_output_bytes"]:
                raise ResourceError("input byte limit exceeded")
    if manifest is not None:
        if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), dict) or not isinstance(manifest.get("entity_files"), dict):
            raise ValueError("invalid dataset manifest")
        for relative, metadata in manifest["files"].items():
            budget.check()
            path = checked_path(root, relative)
            if not path.is_file():
                issues.append(f"missing artifact: {relative}")
                continue
            measure(path)
            checksum = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    budget.check()
                    checksum.update(chunk)
            if not isinstance(metadata, dict) or checksum.hexdigest() != metadata.get("sha256") or path.stat().st_size != metadata.get("bytes"):
                issues.append(f"artifact hash or size differs: {relative}")
        if manifest.get("profile_hash") != digest(profile):
            issues.append("profile differs from the generation manifest")
        entity_files = manifest["entity_files"]
    else:
        base = root / "data" if (root / "data").is_dir() else root
        entity_files = {entity: {kind: str((base / f"{entity}.{kind}").relative_to(root))
                                for kind in ("json", "jsonl", "csv") if (base / f"{entity}.{kind}").is_file()}
                        for entity in profile["entities"]}
    data = {}
    for entity, formats in entity_files.items():
        budget.check()
        if entity not in profile["entities"]:
            issues.append(f"unexpected entity in manifest: {entity}")
            continue
        if not isinstance(formats, dict) or not formats:
            issues.append(f"missing entity files: {entity}")
            continue
        parsed = None
        for kind, relative in formats.items():
            if kind not in ("json", "jsonl", "csv"):
                raise ValueError("unsupported dataset format")
            path = checked_path(root, relative)
            if manifest is not None and relative not in manifest["files"]:
                issues.append(f"unregistered artifact: {relative}")
            measure(path)
            current = read_rows(path, kind, profile["entities"][entity]["fields"])
            if parsed is not None and canonical(current) != canonical(parsed):
                issues.append(f"representations differ: {entity}")
            parsed = current if parsed is None else parsed
        data[entity] = parsed
    negative_path = checked_path(root, "negative/cases.jsonl")
    if negative_path.is_file():
        measure(negative_path)
        cases = [strict_json(line) for line in negative_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        cases = []
    if sum(len(rows) for rows in data.values()) + len(cases) > budget.limits["max_total_rows"]:
        raise ResourceError("input record limit exceeded")
    if manifest is not None and manifest.get("dataset_id") != digest(data):
        issues.append("dataset content differs from the manifest")
    scenario_ids = {entity: [(scenario or {}).get("id") for scenario in schedule(profile, entity)] for entity in profile["entities"]}
    return data, cases, scenario_ids, issues
