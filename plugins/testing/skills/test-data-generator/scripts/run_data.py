import argparse
import json
import sys

from engine.common import ProfileError, ResourceError


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
        from engine.runner import run_isolated
        if args.command == "inspect":
            result = run_isolated("inspect", args.profile, None)
        elif args.command == "generate":
            result = run_isolated("generate", args.profile, args.output_root)
        else:
            result = run_isolated("validate", args.profile, args.dataset)
    except ProfileError as error:
        print(json.dumps({"generation_status": "blocked", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": str(error)}, ensure_ascii=False, allow_nan=False))
        return 2
    except (ImportError, OSError, ValueError, OverflowError, ResourceError, KeyboardInterrupt) as error:
        print(json.dumps({"generation_status": "failed", "validation_status": "not_run",
                          "system_execution_status": "not_run", "error": "interrupted" if isinstance(error, KeyboardInterrupt) else (
                              f"dependency unavailable: {error}" if isinstance(error, ImportError) else str(error))}, ensure_ascii=False, allow_nan=False))
        return 4
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 3 if result["validation_status"] in ("failed", "incomplete") else 0


if __name__ == "__main__":
    sys.exit(main())
