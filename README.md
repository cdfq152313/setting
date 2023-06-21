# 安裝

此設定檔的重點為
1. 設置~/.vimrc (vim的設定檔)
2. 設置~/.zshrc (zsh的設定檔)

直接執行下列程式碼

```bash
cd setting
./setup.sh
```

# 補充說明

## 設定軟連結(以vimrc為例)

家目錄底下的.vimrc為vim的設定檔。
在當前目錄中打以下指令，可以建立一個軟連結將家目錄的.vimrc直接參考到目前資料夾的vimrc。

```bash
ln -fs $PWD/vimrc ~/.vimrc
```

## vim

- [vim-plugin](https://github.com/junegunn/vim-plug):此為vim的套件管理器。
- [nerd-tree](https://github.com/preservim/nerdtree):快捷鍵`ctrl+b`，快速瀏覽檔案工具。
- [nerd-commenter](https://github.com/preservim/nerdcommenter):快捷鍵`ctrl+/`，快速註解反註解。


## zshrc

- [zinit](https://github.com/zdharma-continuum/zinit): zsh套件管理器。
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting): 輸入指令時提示指令有無錯誤。
- [zsh-completions](https://github.com/zsh-users/zsh-completions): 遺漏的自動補完。
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): 指令輸入建議。