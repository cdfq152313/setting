# 安裝

## 下載到家目錄

```bash
cd ~
git clone https://github.com/cdfq152313/setting.git
cd setting
```

之後可以使用 [taskfile](https://taskfile.dev/) 來安裝。

可參考 [taskfile.yml](/Taskfile.yml) 來知道具體動作。


## 安裝常用工具

```
task dep
```

- linux 會使用 apt 安裝常用套件 ( 需在 ubuntu / debian 環境 )
- mac 會使用 brew 安裝常用套件 ( 請先確認已安裝 homebrew )
- windows 會使用 choco 安裝常用套件 ( 請先確認已安裝 chocolatey )
- 不需要安裝的套件可以刪掉

## 安裝 vim plugin
```
task vim
```

- 幫 vim 設定 soft-link
- [vim-plugin (套件管理器)](https://github.com/junegunn/vim-plug)
  - [nerd-tree](https://github.com/preservim/nerdtree):快捷鍵`ctrl+b`，快速瀏覽檔案工具。
  - [nerd-commenter](https://github.com/preservim/nerdcommenter):快捷鍵`ctrl+/`，快速註解反註解。

## 安裝 zsh (mac/linux)
```
task shell
```

- 幫 zsh 設定 soft-link
- zsh 的 config 含有 zoxide，需安裝或註解。
- [powerlevel10k](https://github.com/romkatv/powerlevel10k) : zsh theme
- [antidote (套件管理器)](https://github.com/mattmc3/antidote)
  - [fast-syntax-highlighting](https://github.com/zdharma/fast-syntax-highlighting): 輸入指令時提示指令有無錯誤。
  - [zsh-completions](https://github.com/zsh-users/zsh-completions): 遺漏的自動補完。
  - [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): 指令輸入建議(提示出現後按右鍵補完)。

![image](https://github.com/user-attachments/assets/b35a46b7-96d3-4b36-aacf-fa8633b4956e)


## 安裝 nushell (windows)

```
task shell
```

- 幫 nushell 設定 soft-link。
- nushell 的 config 含有 zoxide 和 starship，需先安裝。

![image](https://github.com/user-attachments/assets/dcd874ed-afe1-403b-a17e-8efea1bebfc1)
  
