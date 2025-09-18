" home/end/pageup/pagedown
noremap H ^
noremap L $
noremap K {
noremap J }

" Redo undo
nnoremap u undo
nnoremap U redo

" not copy action
noremap D "_d
noremap DD "_dd
noremap C "_c
noremap x "_x
noremap X "_X
noremap s "_s
noremap S "_S
vnoremap p pgvy

" tab
vmap > editor.action.indentLines
vmap < editor.action.outdentLines

" search
map / actions.find

" surround
vmap " S"
vmap ' S'
vmap ( S(
vmap [ S[
vmap { S{
vmap a editor.action.smartSelect.expand
vmap z editor.action.smartSelect.shrink

" multiple cursor
vmap n editor.action.moveSelectionToNextFindMatch
vmap N editor.action.moveSelectionToPreviousFindMatch
vmap m editor.action.addSelectionToNextFindMatch
vmap M cursorUndo

" common action 
map <leader>a gitlens.toggleFileBlame
map <leader>r editor.action.rename
map <leader>f editor.action.formatDocument
map <leader>o editor.action.organizeImports
map <leader>h gitlens.views.lineHistory.focus
map <leader>q editor.action.quickFix

" build/run/debug
map <leader>dd workbench.action.debug.start
map <leader>ds workbench.action.debug.stop
map <leader>db editor.debug.action.toggleBreakpoint

" code navigation
map <leader>ne editor.action.marker.nextInFiles

" easy motion
map f extension.aceJump.multiChar

" split window
nmap <tab> workbench.action.focusNextGroup
nmap <leader>\ workbench.action.splitEditorToRightGroup
nmap \ workbench.action.moveEditorToRightGroup
nmap | workbench.action.joinAllGroups
nmap - workbench.action.moveEditorToBelowGroup
nmap _ workbench.action.moveEditorToAboveGroup

" show
map <leader>sd editor.action.showHover
map <leader>sp editor.action.triggerParameterHints
map <leader>sf workbench.action.gotoSymbol

" copilot
map <leader>cc workbench.action.chat.open
