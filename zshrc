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

# Execution time (only avaliable in gallois)
function preexec() {
	timer=${timer:-$SECONDS}
}

function precmd() {
	if [ $timer ]; then
		elapsed_s=$(($SECONDS - $timer))
		if [[ $elapsed_s -ge 30 ]]; then
			local -ri s=$(( elapsed_s%60 ))
			local -ri m=$(( (elapsed_s/60)%60 ))
			local -ri h=$(( (elapsed_s/3600)%24 ))
			local -ri d=$(( elapsed_s/86400 ))
			if (( d > 0 )); then
				timer_show="${d}d${h}h"
			elif (( h > 0 )); then
				timer_show="${h}h${m}m"
			elif (( m > 0 )); then
				timer_show="${m}m${s}s"
			else
				timer_show="${s}s"
			fi
			RPS1="\$(git_custom_status)\$(ruby_prompt_info) %{$fg[red]%}(${timer_show})%f"
		else
			RPS1="\$(git_custom_status)\$(ruby_prompt_info)"
		fi
		unset timer
	else
		RPS1="\$(git_custom_status)\$(ruby_prompt_info)"
	fi
}

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
