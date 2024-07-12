" Install vim-plug if not found
if !has("win32")
  let data_dir = has('nvim') ? stdpath('data') . '/site' : '~/.vim'
  if empty(glob(data_dir . '/autoload/plug.vim'))
    silent execute '!curl -fLo '.data_dir.'/autoload/plug.vim --create-dirs  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
    autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
  endif
endif

" Run PlugInstall if there are missing plugins
autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
  \| PlugInstall --sync | source $MYVIMRC
\| endif

if has("win32")
  call plug#begin('~/vimfiles/bundle')
else
  call plug#begin('~/.vim/plugged')
endif
Plug 'scrooloose/nerdtree'
Plug 'preservim/nerdcommenter'
Plug 'tpope/vim-surround'
if has('nvim')
  Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
endif
call plug#end()

" 編輯喜好設定
set scrolloff=5
set shiftwidth=4 " 設定縮排寬度 = 4
set tabstop=4    " tab 的字元數
set expandtab    " 用 space 代替 tab
set ic           " 設定搜尋忽略大小寫
set ru           " 第幾行第幾個字
set nu           " 顯示行號
set incsearch    " 在關鍵字還沒完全輸入完畢前就顯示結果
set smartindent  " 設定 smartindent
set confirm      " 操作過程有衝突時，以明確的文字來詢問
set history=100  " 保留 100 個使用過的指令
colorscheme torte

" 改變leader key
let mapleader = " "

" NerdTree
nnoremap <F2> :NERDTreeToggle<CR>
" Exit Vim if NERDTree is the only window remaining in the only tab.
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | call feedkeys(":quit\<CR>:\<BS>") | endif
" Close the tab if NERDTree is the only window remaining in it.
autocmd BufEnter * if winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | call feedkeys(":quit\<CR>:\<BS>") | endif
nmap <silent> <F3> :wincmd h<CR>
nmap <silent> <F4> :wincmd l<CR>
nnoremap <F5> :tabprevious<CR>
nnoremap <F6> :tabnext<CR>

" home/end/pageup/pagedown
map <silent> H ^
map <silent> L $
noremap K {
noremap J }

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
