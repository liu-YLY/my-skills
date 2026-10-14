import argparse
import json
import sys

from engine.common import ProfileError
from engine.profile import inspect_profile, load_profile


def main():
    parser = argparse.ArgumentParser(description="Inspect a test-data profile without generating records")
    parser.add_argument("command", choices=["inspect"])
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    try:
        result = inspect_profile(load_profile(args.profile))
    except ProfileError as error:
        print(json.dumps({"generation_status": "blocked", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": str(error)}, ensure_ascii=False))
        return 2
    except (OSError, ValueError, OverflowError) as error:
        print(json.dumps({"generation_status": "failed", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": str(error)}, ensure_ascii=False))
        return 4
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
