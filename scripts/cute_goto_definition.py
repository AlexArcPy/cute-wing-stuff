# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.


from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import guimgr.multieditor
import wingapi

import shared

def cute_goto_definition(editor=wingapi.kArgEditor):
    '''
    Go to the definition of the symbol that the caret is on.
    
    This is an improvement over Wing's `goto-selected-symbol-defn` because if
    operated when selecting a segment of code, it looks at the end of the
    selection instead of the start.
    
    Suggested key combination: `F4`
    '''

    assert isinstance(editor, wingapi.CAPIEditor)
    wingapi.gApplication.ExecuteCommand('set-visit-history-anchor')    
    selection_start, selection_end = editor.GetSelection()
    editor.SetSelection(selection_end, selection_end)
    backup = guimgr.multieditor.CMultiEditor.NextVisitInHistory
    guimgr.multieditor.CMultiEditor.NextVisitInHistory = lambda *args, **kwargs: None
    wingapi.gApplication.ExecuteCommand('goto-selected-symbol-defn')
    guimgr.multieditor.CMultiEditor.NextVisitInHistory = backup
    wingapi.gApplication.ExecuteCommand('set-visit-history-anchor')    