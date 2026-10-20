#!/usr/bin/env bash
# Installs the DASG skill and agents for GitHub Copilot Chat in VS Code (macOS / Linux).
# Run from this folder:  bash install-mac-linux.sh
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$HOME/.claude/skills"
AGENTS="$HOME/.claude/agents"

mkdir -p "$SKILLS" "$AGENTS"
rm -rf "$SKILLS/dasg-protocol-security-review"
cp -R "$SRC/skills/dasg-protocol-security-review" "$SKILLS/"
cp "$SRC"/agents/*.md "$AGENTS/"

echo "Installed:"
find "$SKILLS/dasg-protocol-security-review" -type f | sed 's/^/  /'
ls "$AGENTS"/dasg-*.md | sed 's/^/  /'
echo
echo "Next: in VS Code run 'Developer: Reload Window', then type / in Copilot Chat (Agent mode)."
