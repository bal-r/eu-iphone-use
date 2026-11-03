#!/usr/bin/env python3
"""Named PUA (Phone Use Agent) operations when an MCP binding is unavailable; same runtime guards."""
import argparse
import os
import shutil
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from iphone_use import PUAError, Runtime, SCHEMAS, serve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", nargs="?", choices=["pua_" + name for name in SCHEMAS])
    parser.add_argument("arguments", nargs="?", default="{}", help="JSON object matching the MCP tool schema")
    parser.add_argument("--export-images", help="Explicitly keep returned observation images in this local directory (otherwise deleted at exit)")
    parser.add_argument("--session",action="store_true",help="Persistent stdio MCP session; keeps the lease and observations across calls")
    parser.add_argument("--state-dir")
    parser.add_argument("--url")
    args = parser.parse_args()
    runtime = None
    if args.session:
        if args.tool or args.export_images:parser.error("--session uses stdin MCP requests without a positional tool or image export")
        runtime=Runtime(args.state_dir,args.url)
        try:serve(runtime)
        finally:runtime.close()
        return 0
    if not args.tool:parser.error("Choose a tool, or --session for persistent MCP")
    try:
        arguments = json.loads(args.arguments, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
        runtime = Runtime(args.state_dir, args.url)
        result = runtime.call(args.tool, arguments)
        if args.export_images and runtime.phone.capture_paths:
            with runtime.access.delivery():
                destination = Path(args.export_images).expanduser().resolve()
                destination.mkdir(parents=True, exist_ok=True, mode=0o700)
                replacements = {}
                for source in runtime.phone.capture_paths:
                    target = destination / source.name
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, "wb") as output, source.open("rb") as image:
                        shutil.copyfileobj(image, output)
                    replacements[str(source)] = str(target)
                def exported(value):
                    if isinstance(value, dict): return {k: exported(v) for k, v in value.items()}
                    if isinstance(value, list): return [exported(v) for v in value]
                    return replacements.get(value, value) if isinstance(value, str) else value
                result = exported(result)
    except PUAError as exc:
        result = {"error": exc.as_dict()}
    except (ValueError, TypeError) as exc:
        result = {"error": {"code": "invalid_argument", "message": str(exc), "uncertain": False}}
    finally:
        if runtime:
            runtime.close()
    try:
        if runtime:
            with runtime.access.delivery():
                print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        else:
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    except PUAError as exc:
        result = {"error": exc.as_dict()}
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 1 if "error" in result or (args.tool == "pua_ready" and result.get("ready") is not True) else 0


if __name__ == "__main__":
    sys.exit(main())
