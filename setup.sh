set -x
if [[ "$OSTYPE" == "linux-gnu" ]]; then
	sudo apt install vim ack-grep htop curl zsh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OSX
	brew tap dart-lang/dart
	brew install dart git vim zsh
fi

curl -L git.io/antigen > ~/.antigen.zsh

ln -fs $(pwd)/vimrc ~/.vimrc
ln -fs $(pwd)/zshrc ~/.zshrc
