#!/usr/bin/env bash

set -euo pipefail

args="$@"
stdout=""

error_handler() {
    local exit_code=$?
    local line_number=$1
    echo "Script failed at line $line_number with exit code $exit_code"
    echo "$stdout"
}

trap 'error_handler $LINENO' ERR

if [[ ! -d venv ]]; then
    echo "Create python virtual environment, .venv..."
    stdout=$(python3 -m venv .venv 2>&1)
fi

echo "Source python virtual environment, .venv..."
source .venv/bin/activate

echo "Install python requirements..."
stdout=$(pip install --requirement requirements.txt 2>&1)

echo "Install ansible requirements..."
stdout=$(ansible-galaxy install --role-file requirements.yml 2>&1)

echo "Lint ansible..."
stdout=$(ansible-lint 2>&1)

if [[ -n "$args" ]]; then
    echo "Run $([[ -n "$args" ]] && echo " $args" || true)..."
    ansible-playbook -i ansible_tailscale_inventory.py $args || true
fi
