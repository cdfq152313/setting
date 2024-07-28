# Nushell Environment Config File
#
# version = "0.95.0"

# Environment variables
use std "path add"
match $nu.os-info.name {
    "windows" => {
    }
    "linux" => {
        path add /home/linuxbrew/.linuxbrew/bin
        path add ~/.local/bin
    }
    "macos" => {
        path add /opt/homebrew/bin
    }
}
# Uncomment it when git is chinese
# $env.LANG = "en_US.UTF-8"

# Shell prompt
$env.STARSHIP_CONFIG = ([$nu.home-path 'setting' 'nushell' 'starship.toml'] | path join)
export-env { $env.STARSHIP_SHELL = "nu"; load-env {
    STARSHIP_SESSION_KEY: (random chars -l 16)
    PROMPT_MULTILINE_INDICATOR: (
        starship prompt --continuation
    )

    # Does not play well with default character module.
    # TODO: Also Use starship vi mode indicators?
    PROMPT_INDICATOR: ""

    PROMPT_COMMAND: {||
        # jobs are not supported
        (
            starship prompt
                --cmd-duration $env.CMD_DURATION_MS
                $"--status=($env.LAST_EXIT_CODE)"
                --terminal-width (term size).columns
        )
    }

    config: ($env.config? | default {} | merge {
        render_right_prompt_on_last_line: true
    })

    PROMPT_COMMAND_RIGHT: {||
        (
            starship prompt
                --right
                --cmd-duration $env.CMD_DURATION_MS
                $"--status=($env.LAST_EXIT_CODE)"
                --terminal-width (term size).columns
        )
    }
}}

# Specifies how environment variables are:
# - converted from a string to a value on Nushell startup (from_string)
# - converted from a value back to a string when running external commands (to_string)
# Note: The conversions happen *after* config.nu is loaded
$env.ENV_CONVERSIONS = {
    "PATH": {
        from_string: { |s| $s | split row (char esep) | path expand --no-symlink }
        to_string: { |v| $v | path expand --no-symlink | str join (char esep) }
    }
    "Path": {
        from_string: { |s| $s | split row (char esep) | path expand --no-symlink }
        to_string: { |v| $v | path expand --no-symlink | str join (char esep) }
    }
}

# Directories to search for scripts when calling source or use
# The default for this is $nu.default-config-dir/scripts
$env.NU_LIB_DIRS = [
    ($nu.default-config-dir | path join 'scripts') # add <nushell-config-dir>/scripts
    ($nu.data-dir | path join 'completions') # default home for nushell completions
]

# Directories to search for plugin binaries when calling register
# The default for this is $nu.default-config-dir/plugins
$env.NU_PLUGIN_DIRS = [
    ($nu.default-config-dir | path join 'plugins') # add <nushell-config-dir>/plugins
]

# Alias
source nu_scripts/aliases/git/git-aliases.nu
alias gs = git status
alias vi = vim
alias cat = bat

# Auto-completions
source nu_scripts/custom-completions/curl/curl-completions.nu
source nu_scripts/custom-completions/docker/docker-completions.nu
source nu_scripts/custom-completions/flutter/flutter-completions.nu
source nu_scripts/custom-completions/git/git-completions.nu
source nu_scripts/custom-completions/less/less-completions.nu
source nu_scripts/custom-completions/make/make-completions.nu
source nu_scripts/custom-completions/npm/npm-completions.nu
source nu_scripts/custom-completions/rustup/rustup-completions.nu
source nu_scripts/custom-completions/scoop/scoop-completions.nu
source nu_scripts/custom-completions/tar/tar-completions.nu
source nu_scripts/custom-completions/tcpdump/tcpdump-completions.nu
source nu_scripts/custom-completions/ssh/ssh-completions.nu

# zoxide
zoxide init nushell | save -f ~/.zoxide.nu
