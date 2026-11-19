#!/bin/bash
# Wrapper: ./install.sh "/path/to/Buckshot Roulette.exe" [--dest DIR] [--no-shortcut] [--force]
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required (sudo apt install python3)" >&2
    exit 1
fi
exec python3 "$(dirname "$(readlink -f "$0")")/installer.py" "$@"
