" home/end/pageup/pagedown
noremap H ^
noremap L $
noremap K {
noremap J }

" Redo undo
nnoremap u :vsc undo<CR>
nnoremap U :vsc redo<CR>

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
vmap > :vsc editor.action.indentLines<CR>
vmap < :vsc editor.action.outdentLines<CR>

" search
map / :vsc actions.find<CR>

" surround
vmap " S"
vmap ' S'
vmap ( S(
vmap [ S[
vmap { S{
vmap a :vsc editor.action.smartSelect.expand<CR>
vmap z :vsc editor.action.smartSelect.shrink<CR>

" multiple cursor
vmap n editor.action.addSelectionToNextFindMatch
vmap N editor.action.addSelectionToPreviousFindMatch
vmap q editor.action.moveSelectionToNextFindMatch
vmap Q editor.action.moveSelectionToPreviousFindMatch

" common action 
map <leader>a :vsc gitlens.toggleFileBlame<CR>
map <leader>r :vsc editor.action.rename<CR>
map <leader>f :vsc editor.action.formatDocument<CR>
map <leader>o :vsc editor.action.organizeImports<CR>
map <leader>h :vsc gitlens.views.lineHistory.focus<CR>
map <leader>q :vsc editor.action.quickFix<CR>

" build/run/debug
map <leader>dd :vsc workbench.action.debug.start<CR>
map <leader>ds :vsc workbench.action.debug.stop<CR>
map <leader>db :vsc editor.debug.action.toggleBreakpoint<CR>

" test
map <leader>t :vsc pytest-runner.run-test<CR>
map <leader>dt :vsc pytest-runner.run-test-docker<CR>
map <leader>T :vsc pytest-runner.run-module-test<CR>
map <leader>dT :vsc pytest-runner.run-module-test-docker<CR>

" code navigation
nmap gr :vsc references-view.findReferences<CR>
nmap gi :vsc editor.action.goToImplementation<CR>
nmap [d :vsc editor.action.marker.prev<CR>
nmap [D :vsc editor.action.marker.prevInFiles<CR>
nmap ]d :vsc editor.action.marker.next<CR>
nmap ]D :vsc editor.action.marker.nextInFiles<CR>

" easy motion
map f :vsc extension.aceJump.multiChar<CR>

" split window
nmap <tab> :vsc workbench.action.focusNextGroup<CR>
nmap <leader>\ :vsc workbench.action.splitEditorToRightGroup<CR>
nmap \ :vsc workbench.action.moveEditorToRightGroup<CR>
nmap | :vsc workbench.action.joinAllGroups<CR>
nmap - :vsc workbench.action.moveEditorToBelowGroup<CR>
nmap _ :vsc workbench.action.moveEditorToAboveGroup<CR>

" show
map <leader>sd :vsc editor.action.showHover<CR>
map <leader>sp :vsc editor.action.triggerParameterHints<CR>
map <leader>sf :vsc workbench.action.gotoSymbol<CR>

" open sidebar 
nmap <leader>wc :vsc workbench.action.chat.open<CR>
nmap <leader>we :vsc workbench.view.explorer<CR>
nmap <leader>wg :vsc workbench.view.scm<CR>
