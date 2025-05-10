" Install vim-plug if not found
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
endif

" Run PlugInstall if there are missing plugins
autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
  \| PlugInstall --sync | source $MYVIMRC
\| endif

call plug#begin()
Plug 'scrooloose/nerdtree'
Plug 'preservim/nerdcommenter'
Plug 'tpope/vim-surround'
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'terryma/vim-expand-region'
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'
call plug#end()

" 編輯喜好設定
" coc
set encoding=utf-8
set nobackup
set nowritebackup
set updatetime=300
set signcolumn=yes
" other
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

" home/end/pageup/pagedown
map <silent> H ^
map <silent> L $
noremap K {
noremap J }

" Move focus among window/spilt
nnoremap <silent> <F3> :tabprevious<CR>
nnoremap <silent> <F4> :tabnext<CR>
nnoremap <silent> <tab> :wincmd w<CR>
nnoremap <silent> <C-]> <C-I>

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
vmap " S"
vmap ' S'
vmap ( S(
vmap [ S[
vmap { S{
vmap a <Plug>(expand_region_expand)
vmap z <Plug>(expand_region_shrink)


" common action
nnoremap <silent> <leader>r <Plug>(coc-rename)
nnoremap <silent> <leader>f :CocCommand editor.action.formatDocument<CR>
nnoremap <silent> <leader>o :CocCommand editor.action.organizeImport<CR>
nnoremap <silent> <leader>sd :call ShowDocumentation()<CR>
nmap <leader>q  <Plug>(coc-codeaction-cursor)

" code navigation 
nmap <silent> <leader>gd <Plug>(coc-definition)
nmap <silent> <leader>gt <Plug>(coc-type-definition)
nmap <silent> <leader>gi <Plug>(coc-implementation)
nmap <silent> <leader>gr <Plug>(coc-references)

" coc-specific config
" Make <CR> to accept selected completion item or notify coc.nvim to format
" <C-g>u breaks current undo, please make your own choice
inoremap <silent><expr> <TAB> coc#pum#visible() ? coc#pum#confirm()
                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm()
                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

" Highlight the symbol and its references when holding the cursor
autocmd CursorHold * silent call CocActionAsync('highlight')

" Preview function
function! ShowDocumentation()
  if CocAction('hasProvider', 'hover')
    call CocActionAsync('doHover')
  else
    call feedkeys('K', 'in')
  endif
endfunction

