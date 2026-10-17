# dotfiles

Personal Mac setup: Homebrew packages and apps, bash prompt, git config, and one
agent-instructions file shared by Claude Code and Codex. No secrets live here.

## New Mac

Needs only the Mac password. Open Terminal.app, paste this one line, press Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && eval "$(/opt/homebrew/bin/brew shellenv)" && git clone https://github.com/dchudz/dotfiles.git ~/dotfiles && ~/dotfiles/setup.sh
```

It stops twice: Enter and the Mac password for Homebrew, and the Mac password
once more to make bash the login shell. Then it installs everything in the
Brewfile, symlinks the config files into place, points `~/.claude/CLAUDE.md`
at the same instructions file Codex reads, and sets Dock autohide and Finder
list view. It is safe to re-run.

Then, in this order (Chrome first, because the other passwords live in it):

1. Chrome: sign in to Google (approve on the phone if asked); make it the
   default browser when it asks. Passwords sync from here.
2. Open iTerm2; quit Terminal.app. Run `gh auth login --web --hostname github.com --git-protocol https`.
3. Claude: open the app and sign in. In iTerm2 run `claude` once and `/login`.
4. ChatGPT / Codex: open the app and sign in; in iTerm2 run `codex login`.
5. Granola, Wispr Flow: sign in; allow microphone, accessibility, and screen
   recording when macOS asks.
6. PyCharm: sign in with the JetBrains account. Sublime Text: enter the license.
7. `aws configure` if you need it.

Everything else (iTerm2 profile, trackpad, keyboard) stays at macOS defaults.

## Layout

| Path | Lands at |
| --- | --- |
| `Brewfile` | `brew bundle` |
| `bash_profile` | `~/.bash_profile` (symlink) |
| `inputrc` | `~/.inputrc` (symlink): case-insensitive tab completion |
| `gitconfig` | included from `~/.gitconfig` (git rewrites that file, so it cannot be a symlink) |
| `gitignore_global` | `~/.gitignore_global` (symlink) |
| `agents.md` | `~/.codex/AGENTS.md` (symlink); `~/.claude/CLAUDE.md` imports it with `@~/.codex/AGENTS.md` |
| `claude/settings.json` | `~/.claude/settings.json` (symlink) |
| `claude/skills/*` | `~/.claude/skills/*` (symlinks) |
| `codex/config.toml` | `~/.codex/config.toml`, copied once (the Codex app rewrites it) |
