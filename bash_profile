export BASH_SILENCE_DEPRECATION_WARNING=1
eval "$(/opt/homebrew/bin/brew shellenv)"
export PATH="$HOME/.local/bin:$PATH"

# Colored ls with type suffixes and human-readable sizes
export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
alias ls='ls -GFh'

# Git tab completion, from Homebrew git if present, else Apple's command line tools
for f in /opt/homebrew/etc/bash_completion.d/git-completion.bash \
         "$(xcode-select -p 2>/dev/null)/usr/share/git-core/git-completion.bash"; do
  if [ -r "$f" ]; then source "$f"; break; fi
done

# Append every command to ~/.full_history with timestamp, host, and directory
log_history() {
  printf '%s %s %s %s\n' "$(date +%Y-%m-%d--%H-%M-%S)" "$(hostname -s)" "$PWD" \
    "$(history 1 | sed 's/^ *[0-9]* *//')" >> ~/.full_history
}
PROMPT_COMMAND=log_history

# Prompt with colored path (blue) and git branch; * = untracked files, + = modified files
parse_git_branch() {
  local branch status mark
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || return
  [ -z "$branch" ] && return

  status=$(git status --porcelain 2>/dev/null) || return
  mark=""
  if printf '%s\n' "$status" | grep -q '^??'; then
    mark="${mark}*"
  fi
  if printf '%s\n' "$status" | grep -q '^[^?]'; then
    mark="${mark}+"
  fi

  printf " (%s%s)" "$branch" "$mark"
}

PS1='\[\033[34m\]\w\[\033[0m\]$(parse_git_branch) $ '

alias subl='open -a "Sublime Text"'

# Up/down arrows search history by current prefix
if [[ $- == *i* ]]; then
  bind '"\e[A": history-search-backward'
  bind '"\e[B": history-search-forward'
fi
