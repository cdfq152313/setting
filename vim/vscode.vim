" home/end/pageup/pagedown
noremap H ^
noremap L $
noremap K {
noremap J }

" j
nnoremap <leader>j J
vnoremap <leader>j J
nnoremap <leader>J gJ
vnoremap <leader>J gJ

" Redo undo
nnoremap u :vsc undo<CR>
nnoremap U :vsc redo<CR>

" not copy action
noremap x "_x
noremap s "_s
vnoremap p pgvy

" indent/outdent
vnoremap > :vsc editor.action.indentLines<CR>
vnoremap < :vsc editor.action.outdentLines<CR>

" search
nnoremap / :vsc actions.find<CR>

" surround
vmap " S"
vmap ' S'
vmap ( S(
vmap [ S[
vmap { S{
vnoremap a editor.action.smartSelect.expand
vnoremap z editor.action.smartSelect.shrink

" multiple cursor
vnoremap n editor.action.addSelectionToNextFindMatch
vnoremap N editor.action.moveSelectionToPreviousFindMatch
vnoremap m editor.action.moveSelectionToNextFindMatch

" common action
nnoremap <leader>a :vsc gitlens.toggleFileBlame<CR>
nnoremap <leader>r :vsc editor.action.rename<CR>
nnoremap <leader>f :vsc editor.action.formatDocument<CR>
nnoremap <leader>o :vsc editor.action.organizeImports<CR>
nnoremap <leader>h :vsc gitlens.views.lineHistory.focus<CR>
vnoremap <leader>h :vsc gitlens.views.lineHistory.focus<CR>
nnoremap <leader>q :vsc editor.action.quickFix<CR>
nnoremap <leader>w :vsc workbench.action.openView<CR>

" build/run/debug
nnoremap <leader>dd :vsc workbench.action.debug.start<CR>
nnoremap <leader>ds :vsc workbench.action.debug.stop<CR>
nnoremap <leader>db :vsc editor.debug.action.toggleBreakpoint<CR>

" test
nnoremap <leader>t :vsc pytest-runner.run-test<CR>
nnoremap <leader>dt :vsc pytest-runner.run-test-docker<CR>
nnoremap <leader>T :vsc pytest-runner.run-module-test<CR>
nnoremap <leader>dT :vsc pytest-runner.run-module-test-docker<CR>

" code navigation
nnoremap gd :vsc editor.action.revealDefinition<CR>
nnoremap gr :vsc references-view.findReferences<CR>
nnoremap gi :vsc editor.action.goToImplementation<CR>
nnoremap [d :vsc editor.action.marker.prev<CR>
nnoremap [D :vsc editor.action.marker.prevInFiles<CR>
nnoremap ]d :vsc editor.action.marker.next<CR>
nnoremap ]D :vsc editor.action.marker.nextInFiles<CR>

" easy motion
nnoremap f :vsc extension.aceJump.multiChar<CR>

" split window
nnoremap <leader>\ :vsc workbench.action.splitEditorToRightGroup<CR>
nnoremap \ :vsc workbench.action.moveEditorToRightGroup<CR>
nnoremap | :vsc workbench.action.joinAllGroups<CR>
nnoremap - :vsc workbench.action.moveEditorToBelowGroup<CR>
nnoremap _ :vsc workbench.action.moveEditorToAboveGroup<CR>
nnoremap <leader>bo :vsc workbench.action.closeOtherEditors<CR>

" show
nnoremap <leader>sd :vsc editor.action.showHover<CR>
nnoremap <leader>sp :vsc editor.action.triggerParameterHints<CR>
nnoremap <leader>sf :vsc workbench.action.gotoSymbol<CR>
