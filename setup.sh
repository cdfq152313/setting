#curl https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh | sh
PWD=$(pwd)
ln -fs $PWD/vimrc ~/.vimrc
echo ". $PWD/bash_prompt.sh" >> ~/.bashrc
