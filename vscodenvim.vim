" Install vim-plug if not found
let data_dir = has('nvim') ? stdpath('data') . '/site' : '~/.vim'
if empty(glob(data_dir . '/autoload/plug.vim'))
  silent execute '!curl -fLo '.data_dir.'/autoload/plug.vim --create-dirs  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Run PlugInstall if there are missing plugins
autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
  \| PlugInstall --sync | source $MYVIMRC
\| endif

call plug#begin('~/.vim/plugged')
Plug 'tpope/vim-sensible'
Plug 'tpope/vim-surround'
Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
call plug#end()

let mapleader=" "
set scrolloff=5

" home/end/pageup/pagedown
map H ^
map L $
map K {
map J }

" not copy action
noremap x "_x
noremap s "_s
vnoremap p pgvy

if exists('g:vscode')
  let code = v:lua.require("vscode")
  " common action
  map <leader>r  <cmd>call code.call('editor.action.rename')<cr>
  map <leader>f <cmd>call code.call('editor.action.formatDocument')<cr>
  map <leader>o <cmd>call code.call('editor.action.organizeImports')<cr>
  map <leader>sd <cmd>call code.call('editor.action.showHover')<cr>
  map <leader>sf <cmd>call code.call('outline.focus')<cr>
  map <leader>h <cmd>call code.call('gitlens.views.lineHistory.focus')<cr>
  map <leader>q <cmd>call code.call('editor.action.quickFix')<cr>

endif
