#!/bin/bash
# Backward-compatible wrapper. Canonical installer lives in tools/bootstrap/install-git-hooks.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/install-git-hooks.sh"
