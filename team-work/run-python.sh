#!/usr/bin/env bash
# Reuse one installed environment. This script never clones or installs anything.
set -euo pipefail
team_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
shared_dir="$(dirname -- "$team_dir")/shared-local"
kit_dir="${CATAN_KIT_DIR:-$shared_dir/organizer-kit}"
python_bin="${CATAN_PYTHON:-$shared_dir/.venv/bin/python}"
if [[ ! -x "$python_bin" || ! -f "$kit_dir/catan_kit/__init__.py" ]]; then
    printf '%s\n' 'Shared Python or organizer kit not found.' 'Set CATAN_PYTHON and CATAN_KIT_DIR to your existing local installation.' >&2
    exit 1
fi
export PYTHONPATH="$kit_dir${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
exec "$python_bin" "$@"
