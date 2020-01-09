# antigen: https://github.com/zsh-users/antigen
source $HOME/.antigen.zsh

# Load the oh-my-zsh's library.
antigen use oh-my-zsh

# Bundles from the default repo (robbyrussell's oh-my-zsh).
antigen bundle git
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle zsh-users/zsh-completions
antigen bundle zsh-users/zsh-autosuggestions

# Load the theme.
antigen theme gallois

# Tell Antigen that you're done.
antigen apply

# This speeds up pasting w/ autosuggest
# https://github.com/zsh-users/zsh-autosuggestions/issues/238
pasteinit() {
  OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
  zle -N self-insert url-quote-magic # I wonder if you'd need `.url-quote-magic`?
}

pastefinish() {
  zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish

# Export
# export PATH=/usr/local/bin:$PATH
export PATH=$HOME/development/flutter/bin:$PATH
export PATH=$HOME/bin:$PATH
# export PATH=$HOME/.pub-cache/bin:$PATH

# If Vim has error message 'Warning: Failed to set locale category LC_NUMERIC to en_TW.'. Uncomment it.
# export LC_ALL=en_US.UTF-8

# Alias
alias gs="git status"
alias fgen="flutter packages pub run build_runner build  --delete-conflicting-outputs"
alias fget="flutter packages pub get"
# alias tget="tool/get"
# alias tgen="tool/gen"
