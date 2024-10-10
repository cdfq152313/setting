set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

_list:
    just --list

# install dependencies, setup vim and nushell.
[windows]
all: dep vim nu

# install dependencies, setup vim and zsh.
[linux]
[macos]
all: dep vim zsh

# install dependencies
[windows]
dep:
    choco install nushell vim git gsudo vscode godot-mono dotnet-sdk jetbrainstoolbox starship bat zoxide

# install dependencies
[linux]
dep:
    sudo apt update
    sudo apt install git vim zsh zoxide bat

# install dependencies
[macos]
dep:
    brew install git vim zoxide bat

# setup vim
[windows]
vim:
    if (-Not (Test-Path -Path '{{home_dir()}}\vimfiles\autoload')) { \
        New-Item -ItemType Directory -Path '{{home_dir()}}\vimfiles\autoload'; \
        Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim' -OutFile '{{home_dir()}}\vimfiles\autoload\plug.vim'; \
    }
    [IO.File]::WriteAllLines('{{home_dir()}}\.vimrc', 'source {{justfile_dir()}}\vim\vim.vim')
    [IO.File]::WriteAllLines('{{home_dir()}}\.ideavimrc', 'source {{justfile_dir()}}\vim\idea_win.vim')

# setup vim
[linux]
vim:
    ln -fs {{justfile_dir()}}/vim/vim.vim {{home_dir()}}/.vimrc
    ln -fs {{justfile_dir()}}/vim/idea_win.vim {{home_dir()}}/.ideavimrc

# setup vim
[macos]
vim:
    ln -fs {{justfile_dir()}}/vim/vim.vim {{home_dir()}}/.vimrc
    ln -fs {{justfile_dir()}}/vim/idea_mac.vim {{home_dir()}}/.ideavimrc


# setup nushell
[windows]
nu:
    git submodule update --recursive --remote --init
    [IO.File]::WriteAllLines('{{home_dir()}}\AppData\Roaming\nushell\env.nu', 'source {{justfile_dir()}}\nushell\env.nu')
    [IO.File]::WriteAllLines('{{home_dir()}}\AppData\Roaming\nushell\config.nu', 'source {{justfile_dir()}}\nushell\config.nu')

# setup zsh
[linux]
[macos]
zsh:
    ln -fs {{justfile_dir()}}/zsh/zshrc {{home_dir()}}/.zshrc
    ln -fs {{justfile_dir()}}/zsh/zsh_plugins.txt {{home_dir()}}/.zsh_plugins.txt
    ln -fs {{justfile_dir()}}/zsh/p10k.zsh {{home_dir()}}/.p10k.zsh
