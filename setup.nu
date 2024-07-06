
def "main sdk" [] {
    def brew_essential [] {
        brew install vim git fvm pyenv pipx
        pipx ensurepath
        pipx install poetry
    }

    match $nu.os-info.name {
        "windows" => { 
            choco install vim git gsudo vscode godot-mono dotnet-sdk jetbrainstoolbox
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


def "main vim" [] {
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

def "main shell" [] {
    git submodule update --recursive --remote
    match $nu.os-info.name {
        "windows" => { 
            choco install starship
            echo "source ~/setting/env.nu" | save -f $nu.env-path
        }
        _ => { 
            brew install starship
            ln -fs $"($env.PWD)/env.nu" $nu.env-path
        }
    }
} 

def main [] {}