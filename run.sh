#!/usr/bin/env bash
# Launch PyMusic with the project's virtualenv.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python run.py "$@"
