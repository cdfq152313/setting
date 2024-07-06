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
Plug 'tpope/vim-sensible'
Plug 'scrooloose/nerdtree'
Plug 'preservim/nerdcommenter'
Plug 'tpope/vim-surround'
if has('nvim')
  Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
endif
call plug#end()

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
