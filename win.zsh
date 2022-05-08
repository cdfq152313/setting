function __git_prompt_git() {
  GIT_OPTIONAL_LOCKS=0 command git.exe "$@"
}
alias git="git.exe"
