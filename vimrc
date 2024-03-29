" install vim-plug
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
Plug 'scrooloose/nerdtree'
Plug 'preservim/nerdcommenter'
Plug 'tpope/vim-surround'
call plug#end()

" 改變leader key
let mapleader = " "
" 檔案編碼
set encoding=utf-8
set fileencodings=utf-8,cp950
" 編輯喜好設定
set nocompatible " VIM 不使用和 VI 相容的模式
set scrolloff=5
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

" open window
map <F2> :NERDTreeToggle<CR>

" home/end/pageup/pagedown
map <silent> S <Home>
map <silent> L <End>
map <silent> K <PageUp>
map <silent> J <PageDown>

" Move focus among window/spilt
nnoremap <silent> <A-Left> :tabp<CR>
nnoremap <silent> <A-Right> :tabn<CR>
nnoremap <silent> <S-Up> :wincmd k<CR>
nnoremap <silent> <S-Down> :wincmd j<CR>
nnoremap <silent> <S-Left> :wincmd h<CR>
nnoremap <silent> <S-Right> :wincmd l<CR>

" not copy action
noremap D "_d
noremap DD "_dd
noremap C "_c
noremap x "_x
noremap X "_X
noremap s "_s
noremap S "_S
vnoremap p pgvy

" nerdcommenter
nmap <silent> <C-_> <leader>c<space>
vmap <silent> <C-_> <leader>c<space>

" surround
vnoremap " "zc"<C-R>z"<Esc>
vnoremap ' "zc'<C-R>z'<Esc>
vnoremap ( "zc(<C-R>z)<Esc>
vnoremap [ "zc[<C-R>z]<Esc>
vnoremap { "zc{<C-R>z}<Esc>
