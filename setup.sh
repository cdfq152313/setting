set -x
# install package
case `uname` in
  Darwin)
    brew install git vim zsh zoxide bat 
  ;;
  Linux)
    sudo apt install git vim zsh zoxide bat
  ;;
esac

ln -fs $(pwd)/vim/vim.vim ~/.vimrc
ln -fs $(pwd)/zsh/zshrc ~/.zshrc
ln -fs $(pwd)/zsh/zsh_plugins.txt ~/.zsh_plugins.txt
ln -fs $(pwd)/zsh/p10k.zsh ~/.p10k.zsh

