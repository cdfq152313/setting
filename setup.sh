set -x
# install package
if [[ "$OSTYPE" == "linux-gnu" ]]; then
	sudo apt install vim zsh unzip build-essential 
elif [[ "$OSTYPE" == "darwin"* ]]; then
	brew install vim zsh
fi
brew tap leoafarias/fvm
brew install git git-gui repo htop fvm ripgrep exa bat zoxide fzf

bash -c "$(curl --fail --show-error --silent --location https://raw.githubusercontent.com/zdharma-continuum/zinit/HEAD/scripts/install.sh)"

ln -fs $(pwd)/vimrc ~/.vimrc
if [[ "$OSTYPE" == "darwin"* ]]; then
	ln -fs $(pwd)/ideavimrc_mac ~/.ideavimrc
fi 
ln -fs $(pwd)/zshrc ~/.zshrc
ln -fs $(pwd)/zimrc ~/.zimrc
ln -fs $(pwd)/p10k.zsh ~/.p10k.zsh

echo 'Restart your terminal and execute `zimfw install` to apply zsh config'
