
def "main sdk" [] {
    def brew_essential [] {
        brew install vim git fvm pyenv pipx starship
        pipx ensurepath
        pipx install poetry
    }

    match $nu.os-info.name {
        "windows" => { 
            choco install vim git gsudo vscode godot-mono dotnet-sdk jetbrainstoolbox starship
        }
        "linux" => { 
            brew_essential
        }
        "macos" => {
            brew_essential
            brew install --cask docker
            brew install --cask visual-studio-code
            brew install --cask jetbrains-toolbox
        }
    }
}


def "main vim" [] {
    match $nu.os-info.name {
        "windows" => {
            if not ("~/vimfiles/autoload" | path exists ) {
                mkdir ~/vimfiles/autoload
                http get https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim | save -f ~/vimfiles/autoload/plug.vim
            }
            echo "source ~/setting/vim/vim.vim" | save -f ~/.vimrc
            echo "source ~/setting/vim/idea_win.vim" | save -f ~/.ideavimrc
        }
        "linux" => {
            ln -fs $"($env.PWD)/vim/vim.vim" ~/.vimrc
            ln -fs $"($env.PWD)/vim/idea_win.vim" ~/.ideavimrc
        }
        "macos" => {
            ln -fs $"($env.PWD)/vim/vim.vim" ~/.vimrc
            ln -fs $"($env.PWD)/vim/idea_mac.vim" ~/.ideavimrc
        }
    }
}

def "main shell" [] {
    git submodule update --recursive --remote --init
    echo $"source ($env.PWD | path join 'nushell' 'env.nu' )" | save -f $nu.env-path
    echo $"source ($env.PWD | path join 'nushell' 'config.nu' )" | save -f $nu.config-path
    if $nu.os-info.name != "windows" {
        ln -fs $"($env.PWD)/zsh/zshrc" ~/.zshrc
        ln -fs $"($env.PWD)/zsh/zimrc" ~/.zimrc
        ln -fs $"($env.PWD)/zsh/p10k.zsh" ~/.p10k.zsh
    }
} 

def main [] {}