#!/bin/sh
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$task_root"
task_test_state=$(mktemp -d "${TMPDIR:-/tmp}/balta-iphone-tests.XXXXXX")
trap 'rm -rf -- "$task_test_state"' EXIT
export IPHONE_USE_STATE_DIR="$task_test_state"
python3 -m unittest discover -s tests -v
python3 scripts/package.py --validate-only
node --check tooling/forward.mjs
node --check tooling/proxy.mjs
node --test tooling/tests/*.test.mjs
node --check tooling/screen-stream.mjs
python3 scripts/check_screen_ui.py
