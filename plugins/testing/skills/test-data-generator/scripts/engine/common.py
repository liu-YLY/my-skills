import hashlib
import json
import random
import re
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


class ProfileError(ValueError):
    pass


class ResourceError(RuntimeError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def engine_fingerprint(root):
    files = [root / "scripts/run_data.py", *sorted((root / "scripts/engine").glob("*.py")), *sorted((root / "schemas").glob("*.json"))]
    return digest({str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files})


def json_equal(left, right):
    """Compare JSON values without Python's bool/int equivalence."""
    try:
        return canonical(left) == canonical(right)
    except (TypeError, ValueError):
        return False


def strict_json(value):
    def reject_constant(token):
        raise ValueError(f"nonfinite JSON number: {token}")
    return json.loads(value, parse_constant=reject_constant)


def random_for(seed, *parts):
    return random.Random(int(digest([seed, *parts]), 16))


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        raise ValueError("expected an RFC 3339 timestamp with timezone")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def decimal_value(value):
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("decimal values must be strings of at most 64 characters")
    if not re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", value):
        raise ValueError("decimal values must use ordinary decimal notation")
    try:
        parsed = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("invalid decimal") from error
    if not parsed.is_finite():
        raise ValueError("decimal must be finite")
    return parsed


def typed(value, field):
    kind = field["type"]
    if value is None:
        return field.get("nullable", False)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "string":
        return isinstance(value, str)
    try:
        if kind == "decimal":
            decimal_value(value)
        elif kind == "datetime":
            timestamp(value)
        else:
            return False
    except (ValueError, OverflowError):
        return False
    return True


def comparable(value, field):
    if value is None:
        return None
    if field["type"] == "decimal":
        return decimal_value(value)
    if field["type"] == "datetime":
        return timestamp(value)
    return value


class Budget:
    def __init__(self, limits):
        self.started = time.monotonic()
        self.limits = limits
        self.generated_bytes = 0

    def check(self):
        if time.monotonic() - self.started > self.limits["timeout_seconds"]:
            raise ResourceError("execution timeout exceeded")

    def consume_record(self, row):
        self.generated_bytes += len(canonical(row).encode("utf-8"))
        if self.generated_bytes > self.limits["max_output_bytes"]:
            raise ResourceError("generated data byte limit exceeded")
