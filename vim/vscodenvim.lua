local vimrc = vim.fn.stdpath("config") .. "/plugin.vim"
vim.cmd.source(vimrc)

-- let vscode = require('vscode')

-- vim.g.mapleader = " "

-- -- home/end/pageup/pagedown
-- vim.keymap.set({'n','v'}, 'H', '^', {remap = true})
-- vim.keymap.set({'n','v'}, 'L', '$', {remap = true})
-- vim.keymap.set({'n','v'}, 'K', '{', {remap = true})
-- vim.keymap.set({'n','v'}, 'J', '}', {remap = true})

-- -- not copy action
-- vim.keymap.set({'n','v'}, 's', '"_s')
-- vim.keymap.set({'n','v'}, 'x', '"_x')
-- vim.keymap.set('v', 'p', 'pgvy')

-- if vim.g.vscode then
--     -- vim.keymap.set({'n','v'}, '<Leader>r', 'code.action("editor.action.rename")')
-- end
