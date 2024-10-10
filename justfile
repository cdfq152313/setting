set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# list all tasks
list:
    just --list

# install dependencies
[windows]
dep:
    choco install nushell vim git gsudo vscode godot-mono dotnet-sdk jetbrainstoolbox starship bat zoxide

# install dependencies
[linux]
dep:
    sudo apt update
    sudo apt install git vim zsh zoxide bat

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
[macos]
vim:
    ln -fs {{justfile_dir()}}/vim/vim.vim {{home_dir()}}/.vimrc
    ln -fs {{justfile_dir()}}/vim/idea_win.vim {{home_dir()}}/.ideavimrc

# setup nushell
[windows]
nu:
    git submodule update --recursive --remote --init
    [IO.File]::WriteAllLines('{{home_dir()}}\AppData\Roaming\nushell\env.nu', 'source {{justfile_dir()}}\nushell\env.nu')
    [IO.File]::WriteAllLines('{{home_dir()}}\AppData\Roaming\nushell\config.nu', 'source {{justfile_dir()}}\nushell\config.nu')

[linux]
link-zsh:
    ln -fs $(pwd)/zsh/zshrc ~/.zshrc
    ln -fs $(pwd)/zsh/zsh_plugins.txt ~/.zsh_plugins.txt
    ln -fs $(pwd)/zsh/p10k.zsh ~/.p10k.zsh
