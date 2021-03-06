" install vim-plug
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
Plug 'scrooloose/nerdtree'
Plug 'preservim/nerdcommenter'
call plug#end()

" 檔案編碼
set encoding=utf-8
set fileencodings=utf-8,cp950
" 編輯喜好設定
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

" open window
map <C-b> :NERDTreeToggle<CR>

" Move focus among window/spilt
nnoremap <silent> <F3> :tabp<CR>
nnoremap <silent> <F4> :tabn<CR>
nnoremap <silent> <A-h> :tabp<CR>
nnoremap <silent> <A-l> :tabn<CR>
nnoremap <silent> <A-Left> :tabp<CR>
nnoremap <silent> <A-Right> :tabn<CR>

nnoremap <silent> <C-F3> :wincmd h<CR>
nnoremap <silent> <C-F4> :wincmd h<CR>
nnoremap <silent> <C-Up> :wincmd k<CR>
nnoremap <silent> <C-Down> :wincmd j<CR>
nnoremap <silent> <C-Left> :wincmd h<CR>
nnoremap <silent> <C-Right> :wincmd l<CR>
nnoremap <silent> <C-k> :wincmd k<CR>
nnoremap <silent> <C-j> :wincmd j<CR>
nnoremap <silent> <C-h> :wincmd h<CR>
nnoremap <silent> <C-l> :wincmd l<CR>

nmap <silent> <S-F3> <C-o>
nmap <silent> <S-F4> <C-i>
nmap <silent> <S-Left> <C-o>
nmap <silent> <S-Right> <C-i>
nmap <silent> <S-h> <C-o>
nmap <silent> <S-l> <C-i>

" nerdcommenter
nmap <silent> <C-_> <leader>c<space>
vmap <silent> <C-_> <leader>c<space>
