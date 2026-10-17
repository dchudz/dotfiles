# dotfiles

Personal Mac setup: Homebrew packages and apps, bash prompt, git config, and one
agent-instructions file shared by Claude Code and Codex. No secrets live here.

## New Mac

Open Terminal.app, paste this one line, press Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" && eval "$(/opt/homebrew/bin/brew shellenv)" && brew install gh && gh auth login --web --hostname github.com --git-protocol https && gh repo clone dchudz/dotfiles ~/dotfiles && ~/dotfiles/setup.sh
```

It will stop for you four times: Enter and the Mac password for Homebrew,
Enter to open the browser for GitHub login (approve there), the Mac password
once more for the login shell. Then it installs everything in the Brewfile,
symlinks the config files into place, points `~/.claude/CLAUDE.md` at the same
instructions file Codex reads, makes bash the login shell, and sets Dock
autohide and Finder list view. It is safe to re-run.

Then the sign-ins, which cannot be scripted:

1. Open iTerm2 (bash, the prompt from `bash_profile`). Quit Terminal.app.
2. Chrome: sign in; make it the default browser when it asks.
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
| `gitconfig` | included from `~/.gitconfig` (git rewrites that file, so it cannot be a symlink) |
| `gitignore_global` | `~/.gitignore_global` (symlink) |
| `agents.md` | `~/.codex/AGENTS.md` (symlink); `~/.claude/CLAUDE.md` imports it with `@~/.codex/AGENTS.md` |
| `claude/settings.json` | `~/.claude/settings.json` (symlink) |
| `claude/skills/*` | `~/.claude/skills/*` (symlinks) |
| `codex/config.toml` | `~/.codex/config.toml`, copied once (the Codex app rewrites it) |
