set -x
# install package
sudo apt install git vim zsh unzip build-essential htop

curl -fsSL https://raw.githubusercontent.com/zimfw/install/master/install.zsh | zsh

ln -fs $(pwd)/vim/vim.vim ~/.vimrc
ln -fs $(pwd)/zsh/zshrc ~/.zshrc
ln -fs $(pwd)/zsh/zimrc ~/.zimrc
ln -fs $(pwd)/zsh/p10k.zsh ~/.p10k.zsh

echo 'Restart your terminal and execute `zimfw install` to apply zsh config'
