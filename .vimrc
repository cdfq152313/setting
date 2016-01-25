" 檔案編碼
set encoding=utf-8
set fileencodings=utf-8,cp950
" 編輯喜好設定 
syntax on        " 語法上色顯示
set nocompatible " VIM 不使用和 VI 相容的模式
"set ai           " 自動縮排
set shiftwidth=4 " 設定縮排寬度 = 4
set tabstop=4    " tab 的字元數
"set expandtab   " 用 space 代替 tab

set ruler        " 顯示右下角設定值
set backspace=2  " 在 insert 也可用 backspace
set ic           " 設定搜尋忽略大小寫
set ru           " 第幾行第幾個字
set nu           " 顯示行號
set hlsearch     " 設定高亮度顯示搜尋結果
set incsearch    " 在關鍵字還沒完全輸入完畢前就顯示結果
set smartindent  " 設定 smartindent
set confirm      " 操作過程有衝突時，以明確的文字來詢問
set history=100  " 保留 100 個使用過的指令
set laststatus=2
colorscheme torte
" copy paste to terminal
nnoremap <silent> <F9> :set paste<CR>


" Note: Skip initialization for vim-tiny or vim-small.
if !1 | finish | endif

if has('vim_starting')
  if &compatible
    set nocompatible               " Be iMproved
  endif

" Required:
  set runtimepath+=~/.vim/bundle/neobundle.vim/
endif

" Required:
call neobundle#begin(expand('~/.vim/bundle/'))

" Let NeoBundle manage NeoBundle
" Required:
NeoBundleFetch 'Shougo/neobundle.vim'

" My Bundles here:
" Refer to |:NeoBundle-examples|.
" Note: You don't set neobundle setting in .gvimrc!
NeoBundle 'scrooloose/nerdtree'
NeoBundle 'jistr/vim-nerdtree-tabs'
NeoBundle 'scrooloose/nerdcommenter'
NeoBundle 'vim-scripts/cscope_macros.vim'
NeoBundle 'vim-scripts/taglist.vim'
NeoBundle 'vim-scripts/CCTree'
NeoBundle 'kien/ctrlp.vim'
NeoBundle 'mileszs/ack.vim'

call neobundle#end()

" Required:
filetype plugin indent on

" If there are uninstalled bundles found on startup,
" this will conveniently prompt you to install them.
NeoBundleCheck

" open window 
nnoremap <silent> <F2> :NERDTreeTabsToggle<CR> 
nnoremap <silent> <C-F2> :TlistToggle<CR> 


" Move focus among window/spilt
nnoremap <silent> <F3> :tabp<CR> 
nnoremap <silent> <F4> :tabn<CR> 
nnoremap <silent> <C-F3> :wincmd h<CR> 
nnoremap <silent> <C-F4> :wincmd h<CR> 
nnoremap <silent> <A-Left> :tabp<CR>
nnoremap <silent> <A-Right> :tabn<CR>
nnoremap <silent> <C-Up> :wincmd k<CR> 
nnoremap <silent> <C-Down> :wincmd j<CR> 
nnoremap <silent> <C-Left> :wincmd h<CR> 
nnoremap <silent> <C-Right> :wincmd l<CR> 

" Cscope
nmap <silent> <F5> <C-\>

" tag list
let Tlist_Use_Right_Window = 1
let Tlist_Exit_OnlyWindow = 1

