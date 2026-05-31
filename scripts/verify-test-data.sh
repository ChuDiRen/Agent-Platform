#!/usr/bin/env bash
set -euo pipefail

"/mnt/e/Program Files/Python311/python.exe" -m pytest tests/api/test_test_data.py -q
