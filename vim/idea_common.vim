" default setting
let mapleader=" "
set scrolloff=5

" plugin
set surround
set ReplaceWithRegister
set easymotion

" home/end/pageup/pagedown
nmap H <Action>(EditorLineStart)
vmap H <Action>(EditorLineStartWithSelection)
nmap L <Action>(EditorLineEnd)
vmap L <Action>(EditorLineEndWithSelection)
nmap K <Action>(EditorBackwardParagraph)
vmap K <Action>(EditorBackwardParagraphWithSelection)
nmap J <Action>(EditorForwardParagraph)
vmap J <Action>(EditorForwardParagraphWithSelection)


" Run
map <F5> <Action>(Debug)
if &ide =~? 'JetBrains Rider'
    map <F4> <Action>(RiderUnitTestRunContextAction)
    map <S-F4> <Action>(RiderUnitTestDebugContextAction)
endif

" not copy action
noremap D "_d
noremap DD "_dd
noremap C "_c
noremap x "_x
noremap X "_X
noremap s "_s
noremap S "_S
vmap p gr

" tab
vmap > <Action>(EditorIndentSelection)
vmap < <Action>(EditorUnindentSelection)

" search
map / <Action>(Find)

" surround
vnoremap " "zc"<C-R>z"<Esc>
vnoremap ' "zc'<C-R>z'<Esc>
vnoremap ( "zc(<C-R>z)<Esc>
vnoremap [ "zc[<C-R>z]<Esc>
vnoremap { "zc{<C-R>z}<Esc>
vmap a <Action>(EditorSelectWord)
vmap z <Action>(EditorUnSelectWord)

" multiple cursor
nmap <A-k> <Action>(EditorCloneCaretAbove)
nmap <A-j> <Action>(EditorCloneCaretBelow)
vmap n <Action>(FindNext)
vmap N <Action>(FindPrevious)
vmap m <Action>(SelectNextOccurrence)
vmap M <Action>(UnselectPreviousOccurrence)

" common action
map <leader>a <Action>(Annotate)
map <leader>r <Action>(RenameElement)
map <leader>f <Action>(ReformatCode)
map <leader>o <Action>(OptimizeImports)
map <leader>h <Action>(Vcs.ShowHistoryForBlock)
map <leader>g <Action>(Generate)
map <leader>q <Action>(ShowIntentionActions)
map <S-Space> <Action>(GotoNextError)
map <leader>i <Action>(EditorAddCaretPerSelectedLine)

" build/run/debug
map <leader>dr <Action>(Run)
map <leader>dd <Action>(Debug)
map <leader>ds <Action>(Stop)
map <leader>db <Action>(ToggleLineBreakpoint)

" code navigation
map <leader>ni <Action>(GotoImplementation)
map <leader>ns <Action>(GotoSuperMethod)

" easy motion
map f <Plug>(easymotion-sn)

" split left/right shrink
nmap <tab> <Action>(NextSplitter)
nmap \ <Action>(MoveTabRight)
nmap <leader>\ <Action>(OpenInRightSplit)
nmap <S-\> <Action>(Unsplit)
nmap - <Action>(MoveTabDown)
nmap _ <Action>(Unsplit)

" show
map <leader>sd <Action>(QuickJavaDoc)
map <leader>sf <Action>(FileStructurePopup)
map <leader>se <Action>(ShowErrorDescription)
map <leader>sp <Action>(ParameterInfo)


" extract
map <leader>ev <Action>(IntroduceVariable)
map <leader>ec <Action>(IntroduceConstant)
map <leader>ef <Action>(IntroduceField)
map <leader>em <Action>(ExtractMethod)
map <leader>ep <Action>(IntroduceParameter)
map <leader>ei <Action>(Inline)
map <leader>ew <Action>(Flutter.ExtractWidget)

" tool window action
map <leader>wq <Action>(HideActiveWindow)
map <leader>wf <Action>(ActivateProjectToolWindow)
map <leader>wg <Action>(ActivateCommitToolWindow)
map <leader>ws <Action>(ActivateStructureToolWindow)
map <leader>wr <Action>(ActivateRunToolWindow)
map <leader>wd <Action>(ActivateDebugToolWindow)
map <leader>wt <Action>(ActivateTerminalToolWindow)
if &ide =~? 'JetBrains Rider'
    map <leader>we <Action>(Rider.ProblemsView.ErrorsInSolution)
elseif &ide =~? 'webstorm'
    map <leader>we <Action>(ActivateDartAnalysisToolWindow)
endif

" copilot
map <leader>cc <Action>(copilot.chat.show)
