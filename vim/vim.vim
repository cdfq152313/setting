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

call plug#begin()
Plug 'preservim/nerdtree'
Plug 'preservim/nerdcommenter'
Plug 'tpope/vim-surround'
Plug 'neoclide/coc.nvim', {'branch': 'release'}
Plug 'terryma/vim-expand-region'
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'
Plug 'github/copilot.vim'
Plug 'embear/vim-localvimrc'
Plug 'vim-test/vim-test'
Plug 'airblade/vim-rooter'
Plug 'liuchengxu/vim-which-key'
Plug 'puremourning/vimspector'
Plug 'tpope/vim-dotenv'
Plug 'mg979/vim-visual-multi'
if has('nvim')
    Plug 'sindrets/diffview.nvim'
endif
call plug#end()

" 編輯喜好設定
" coc
set encoding=utf-8
set nobackup
set nowritebackup
set updatetime=300
set signcolumn=yes
" other
set belloff=all
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

" memory localvimrc setting
let g:localvimrc_persistent = 2

" 改變leader key
let g:mapleader = "\<Space>"
nnoremap <silent> <leader> :<c-u>WhichKey '<Space>'<CR>
nnoremap <silent> g :<c-u>WhichKey 'g'<CR>
set timeoutlen=300

" Move focus among window/spilt
nnoremap <silent> <F2> :wincmd w<CR>
nnoremap <silent> <S-F3> :tabprevious<CR>
nnoremap <silent> <F3> :tabnext<CR>

" Nerdtree
nnoremap <silent> <leader>we :NERDTreeToggle<CR>
" Exit Vim if NERDTree is the only window remaining in the only tab.
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | call feedkeys(":quit\<CR>:\<BS>") | endif
" Close the tab if NERDTree is the only window remaining in it.
autocmd BufEnter * if winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | call feedkeys(":quit\<CR>:\<BS>") | endif

" ctrlp
nnoremap <silent> <C-P> :Files<CR>
nnoremap <silent> <leader>p :Commands<CR>
nnoremap <silent> <F1> :Commands<CR>

" home/end/pageup/pagedown
map <silent> H ^
map <silent> L $
noremap K {
noremap J }

" Redo undo
nnoremap U <C-R>

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
nmap <silent> <C-/> <leader>c<space>
vmap <silent> <C-/> <leader>c<space>

" surround
vmap " S"
vmap ' S'
vmap ( S(
vmap [ S[
vmap { S{
vmap a <Plug>(expand_region_expand)
vmap z <Plug>(expand_region_shrink)

" coc plugin
let g:coc_global_extensions = ['coc-json', 'coc-pyright']

" common action
nnoremap <silent> <leader>r <Plug>(coc-rename)
nnoremap <silent> <leader>f :CocCommand editor.action.formatDocument<CR>
nnoremap <silent> <leader>o :CocCommand editor.action.organizeImport<CR>
nnoremap <silent> <leader>sd :call ShowDocumentation()<CR>
nmap <leader>q  <Plug>(coc-codeaction-cursor)

" code navigation 
nmap <silent> gd <Plug>(coc-definition)
nmap <silent> gr <Plug>(coc-references)
nmap <silent> gt <Plug>(coc-type-definition)
nmap <silent> gi <Plug>(coc-implementation)
noremap <silent> gb <C-o>
noremap <silent> gn <C-i>

" coc-specific config
" Make <CR> to accept selected completion item or notify coc.nvim to format
" <C-g>u breaks current undo, please make your own choice
inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm() : "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

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

" vim-test
nnoremap <silent> <leader>t :TestNearest<CR>
nnoremap <silent> <leader>T :TestFile<CR>
nnoremap <silent> <leader>dt :call DebugNearest()<CR>

" debugger
let g:vimspector_install_gadgets = [ 'debugpy' ]
noremap <silent> <F5> :call vimspector#Continue()<CR>
noremap <silent> <leader>db :call vimspector#ToggleBreakpoint()<CR>
noremap <silent> <leader>ds :call vimspector#StepOver()<CR>
noremap <silent> <leader>di :call vimspector#StepInto()<CR>
noremap <silent> <leader>do :call vimspector#StepOut()<CR>
noremap <silent> <leader>dr :call vimspector#RunToCursor()<CR>
noremap <silent> <leader>dc :call vimspector#ClearBreakpoints()<CR>

