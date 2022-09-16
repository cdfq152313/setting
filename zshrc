# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

### Added by Zinit's installer
if [[ ! -f $HOME/.local/share/zinit/zinit.git/zinit.zsh ]]; then
    print -P "%F{33} %F{220}Installing %F{33}ZDHARMA-CONTINUUM%F{220} Initiative Plugin Manager (%F{33}zdharma-continuum/zinit%F{220})…%f"
    command mkdir -p "$HOME/.local/share/zinit" && command chmod g-rwX "$HOME/.local/share/zinit"
    command git clone https://github.com/zdharma-continuum/zinit "$HOME/.local/share/zinit/zinit.git" && \
        print -P "%F{33} %F{34}Installation successful.%f%b" || \
        print -P "%F{160} The clone has failed.%f%b"
fi

source "$HOME/.local/share/zinit/zinit.git/zinit.zsh"
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

# Load a few important annexes, without Turbo
# (this is currently required for annexes)
zinit light-mode for \
    zdharma-continuum/zinit-annex-as-monitor \
    zdharma-continuum/zinit-annex-bin-gem-node \
    zdharma-continuum/zinit-annex-patch-dl \
    zdharma-continuum/zinit-annex-rust

# Powerlevel10k
zinit ice depth=1; zinit light romkatv/powerlevel10k

# zsh plugin
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light zsh-users/zsh-history-substring-search
zinit light zdharma-continuum/fast-syntax-highlighting
zinit load djui/alias-tips

# Oh My Zsh feature 
zinit snippet OMZ::lib/completion.zsh
zinit snippet OMZ::lib/history.zsh
zinit snippet OMZ::lib/key-bindings.zsh
zinit snippet OMZ::lib/theme-and-appearance.zsh
zinit snippet OMZ::plugins/git/git.plugin.zsh

# key binding
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

### End of Zinit's installer chunk

# zoxide
eval "$(zoxide init zsh)"

# Export
export PATH=$HOME/.pub-cache/bin:$PATH
export JAVA_HOME=/home/linuxbrew/.linuxbrew/opt/openjdk@17

# If Vim has error message 'Warning: Failed to set locale category LC_NUMERIC to en_TW.'. Uncomment it.
# export LC_ALL=en_US.UTF-8

# Alias
alias ls="exa"
alias l="exa -al"
alias gs="git status"
alias adb=$HOME/Android/Sdk/platform-tools/adb
case `uname` in
  #Darwin)
	#alias cdh="cd /mnt/c/Users/cdfq1"
  #;;
  Linux)
	alias cdh="cd /mnt/c/Users/cdfq1"
	alias dotnet="dotnet.exe"
	alias ds="dotnet-script.exe"
	alias choco="choco.exe"
	alias gchoco="gsudo choco.exe"
  ;;
esac

function win() {
	source $HOME/setting/win.zsh
}

