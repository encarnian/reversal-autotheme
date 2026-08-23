#!/usr/bin/env bash
set -e

echo "=== Reversal Auto-Theme Installer ==="

USER_MODE=0
if [ "$1" == "--user" ] || [ "$EUID" -ne 0 ]; then
    USER_MODE=1
fi

if [ "$USER_MODE" -eq 1 ]; then
    PREFIX="$HOME/.local"
    echo "Installing for current user in $PREFIX..."
    make user-install USER_PREFIX="$PREFIX"
else
    PREFIX="/usr/local"
    echo "Installing system-wide in $PREFIX (root)..."
    make install PREFIX="$PREFIX"
fi

echo ""
echo "Installation complete!"
echo "Run 'reversal-autotheme --all' or launch 'Reversal Auto-Theme' from your desktop application menu."
