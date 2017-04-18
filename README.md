# 前言

此設定檔的重點為
1. 設置~/.vimrc (vim的設定檔)
2. 設置~/.bashrc (bash的設定檔)

# Vimrc

## 設定.vimrc

家目錄底下的.vimrc為vim的設定檔。
在當前目錄中打以下指令，可以建立一個軟連結將家目錄的.vimrc直接參考到目前資料夾的vimrc。

```bash
ln -fs $PWD/vimrc ~/.vimrc
```

## 安裝NeoBundle

NeoBundle是Vim的套件管理系統，可以在裝vim plugin的時候更輕鬆。
在我自己的vimrc的設定中也有用到不少NeoBundle的功能，所以要裝此套件才能正常使用vimrc。

```bash
curl https://raw.githubusercontent.com/Shougo/neobundle.vim/master/bin/install.sh | sh
```


# 設定.bashrc

## bash prompt

在當前目錄下打以下的指令，可以在將家目錄的.bashrc中加入額外bash_prompt的設定。

```bash
echo ". $PWD/bash_prompt.sh" >> ~/.bashrc
```

## pyenv環境

之前使用python的virtualenv時，沒裝此套件bash會顯示錯誤。
但不確定是否真的為此套件的影響。
若使用virtualenv出現錯誤的可以試著多裝此套件。

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


## bash prompt 之 參考頁面
- https://github.com/pyenv/pyenv-installer
- https://gist.github.com/insin/1425703
