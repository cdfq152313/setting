# 安裝NeoBundle

```bash
curl https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh | sh
```

# 設定vimrc

```bash
ln -fs $PWD/vimrc ~/.vimrc
```

# 設定bash prompt

## pyenv環境

安裝
```bash
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
```

把這段貼到.bashrc之後
```bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

## bash prompt

```bash
ln -fs $PWD/bash_prompt.sh ~/.bash_prompt
echo '. ~/.bash_prompt' >> ~/.bashrc
```

## 參考頁面
- https://github.com/pyenv/pyenv-installer
- https://gist.github.com/romanlevin/5e9422045bb6a5eb6558cbe371cd8635

