#!/bin/bash
# Idempotent. Run from anywhere after cloning: ~/dotfiles/setup.sh
set -euo pipefail
DOT="$(cd "$(dirname "$0")" && pwd)"

if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$(/opt/homebrew/bin/brew shellenv)"
brew bundle --file="$DOT/Brewfile"

link() { mkdir -p "$(dirname "$2")"; ln -sfn "$DOT/$1" "$2"; }
link bash_profile ~/.bash_profile
link inputrc ~/.inputrc
link gitignore_global ~/.gitignore_global
link agents.md ~/.codex/AGENTS.md
link claude/settings.json ~/.claude/settings.json
for s in "$DOT"/claude/skills/*/; do
  s=$(basename "$s"); link "claude/skills/$s" ~/.claude/skills/"$s"
done
for m in "$DOT"/claude/mods/*/; do
  m=$(basename "$m"); link "claude/mods/$m" ~/.claude/mods/"$m"
done

# Claude Code reads ~/.claude/CLAUDE.md; this makes it the same file Codex reads.
printf '@~/.codex/AGENTS.md\n' > ~/.claude/CLAUDE.md

# git rewrites ~/.gitconfig in place (which would replace a symlink), so include instead.
if ! grep -q "$DOT/gitconfig" ~/.gitconfig 2>/dev/null; then
  printf '[include]\n\tpath = %s/gitconfig\n' "$DOT" >> ~/.gitconfig
fi
git lfs install

# The Codex app rewrites its config, so this is a seed, copied once.
[ -e ~/.codex/config.toml ] || cp "$DOT/codex/config.toml" ~/.codex/config.toml

[ "$SHELL" = /bin/bash ] || chsh -s /bin/bash

defaults write com.apple.dock autohide -bool true
defaults write com.apple.finder FXPreferredViewStyle -string Nlsv
killall Dock Finder 2>/dev/null || true

echo "done"
