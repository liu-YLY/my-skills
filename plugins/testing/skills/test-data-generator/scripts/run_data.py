import argparse
import json
import sys

from engine.common import ProfileError, ResourceError
from engine.profile import inspect_profile, load_profile
from engine.runner import run_isolated


def main():
    parser = argparse.ArgumentParser(description="Generate or independently validate offline test data")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "generate", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--profile", required=True)
        if name == "generate":
            command.add_argument("--output-root", required=True)
        elif name == "validate":
            command.add_argument("--dataset", required=True)
    args = parser.parse_args()
    try:
        profile = load_profile(args.profile)
        if args.command == "inspect":
            result = inspect_profile(profile)
        elif args.command == "generate":
            result = run_isolated("generate", profile, args.output_root)
        else:
            result = run_isolated("validate", profile, args.dataset)
    except ProfileError as error:
        print(json.dumps({"generation_status": "blocked", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": str(error)}, ensure_ascii=False, allow_nan=False))
        return 2
    except (OSError, ValueError, OverflowError, ResourceError, KeyboardInterrupt) as error:
        print(json.dumps({"generation_status": "failed", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": "interrupted" if isinstance(error, KeyboardInterrupt) else str(error)}, ensure_ascii=False, allow_nan=False))
        return 4
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 3 if result["validation_status"] in ("failed", "incomplete") else 0


if __name__ == "__main__":
    sys.exit(main())
