
def install_sdk [] {
    def brew_essential [] {
        brew install vim git fvm pyenv pipx
        pipx ensurepath
        pipx install poetry
    }

    match $nu.os-info.name {
        "windows" => { 
            choco install vim git gsudo vscode godot-mono dotnet-sdk jetbrainstoolbox
            choco install starship
        }
        "linux" => { 
            brew_essential
        }
        "macos" => {
            brew_essential
            brew install docker
            brew install --cask visual-studio-code
            brew install --cask jetbrains-toolbox
        }
    }
}


def link [] {
    match $nu.os-info.name {
        "windows" => {
            mkdir ~/vimfiles/autoload/ 
            http get https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim | save -f ~/vimfiles/autoload/plug.vim
            echo "source ~/setting/idea_win.vim" | save -f ~/.ideavimrc
            echo "source ~/setting/vimrc" | save -f ~/.vimrc
        }
        "linux" => {
            ln -fs $"($env.PWD)/vimrc" ~/.vimrc
            ln -fs $"($env.PWD)/idea_win.vim" ~/.ideavimrc
        }
        "macos" => {
            ln -fs $"($env.PWD)/vimrc" ~/.vimrc
            ln -fs $"($env.PWD)/idea_mac.vim" ~/.ideavimrc
        }
    }
}

def shell [] {
    match $nu.os-info.name {
        "windows" => { 
            echo "source ~/setting/config.nu" | save -f $nu.config-path
        }
        _ => { 

        }
    }
} 

shell