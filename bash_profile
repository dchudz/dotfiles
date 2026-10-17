export BASH_SILENCE_DEPRECATION_WARNING=1
eval "$(/opt/homebrew/bin/brew shellenv)"
export PATH="$HOME/.local/bin:$PATH"

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
