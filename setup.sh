set -x
# install package
if [[ "$OSTYPE" == "linux-gnu" ]]; then
	sudo apt install vim zsh unzip build-essential 
elif [[ "$OSTYPE" == "darwin"* ]]; then
	brew install vim zsh git
fi
brew tap leoafarias/fvm
brew install fvm repo ack htop

curl -L git.io/antigen > ~/.antigen.zsh

ln -fs $(pwd)/vimrc ~/.vimrc
if [[ "$OSTYPE" == "darwin"* ]]; then
	ln -fs $(pwd)/ideavimrc_mac ~/.ideavimrc
fi 
ln -fs $(pwd)/zshrc ~/.zshrc
