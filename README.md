# 安裝

下載到家目錄，執行 `setup.sh`

```bash
cd ~
git clone https://github.com/cdfq152313/setting.git
cd setting
./setup.sh
```
Setup 會執行下列動作

- 安裝套件
  - linux 會使用 apt 安裝常用套件
  - mac 會使用 brew 安裝常用套件 (請先確認已安裝 homebrew)
  - 不需要安裝套件可以註解掉安裝部份
- 設定 soft-link
  - 幫 vim 設定 soft-link，用 vim-plugin 做套件管理
  - 幫 zsh 設定 soft-link，用 antidote 做套件管理。p10k 為 theme。

# 補充說明

## 設定軟連結(以vimrc為例)

家目錄底下的.vimrc為vim的設定檔。
在當前目錄中打以下指令，可以建立一個軟連結將家目錄的.vimrc直接參考到目前資料夾的vimrc。

```bash
ln -fs $PWD/vim/vimrc ~/.vimrc
```

## vim

- [vim-plugin](https://github.com/junegunn/vim-plug):此為vim的套件管理器。
- [nerd-tree](https://github.com/preservim/nerdtree):快捷鍵`ctrl+b`，快速瀏覽檔案工具。
- [nerd-commenter](https://github.com/preservim/nerdcommenter):快捷鍵`ctrl+/`，快速註解反註解。


## zshrc

- [antidote](https://github.com/mattmc3/antidote): zsh套件管理器。
- [fast-syntax-highlighting](https://github.com/zdharma/fast-syntax-highlighting): 輸入指令時提示指令有無錯誤。
- [zsh-completions](https://github.com/zsh-users/zsh-completions): 遺漏的自動補完。
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): 指令輸入建議(提示出現後按右鍵補完)。
