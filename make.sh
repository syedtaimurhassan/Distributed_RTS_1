#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "[setup] creating virtual environment at ${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[setup] upgrading pip"
python -m pip install --upgrade pip

if [[ -f "requirements.txt" ]]; then
  echo "[setup] installing requirements from requirements.txt"
  python -m pip install -r requirements.txt
fi

echo "[setup] done"
echo "Activate with: source ${VENV_DIR}/bin/activate"
echo "Run CLI help with: PYTHONPATH=src python -m drts_mp1.cli.main --help"
