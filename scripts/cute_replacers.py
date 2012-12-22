# Copyright 2009-2012 Ram Rachum.
# This program is distributed under the MIT license.


from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import sys
import inspect

import wingapi

import shared

TAB_KEY = 15 if 'linux' in sys.platform else '48' if 'darwin' in sys.platform \
                                                                         else 9


def _cute_general_replace(command_name,
                          editor=wingapi.kArgEditor,
                          app=wingapi.kArgApplication):
    assert isinstance(editor, wingapi.CAPIEditor)
    assert isinstance(app, wingapi.CAPIApplication)
    selection_start, selection_end = editor.GetSelection()
    selection = editor.GetDocument().GetCharRange(selection_start,
                                                  selection_end)
    
    if selection:
        editor.SetSelection(selection_start, selection_start)
        app.ExecuteCommand(command_name)
        if shared.autopy_available:
            import autopy.key
            autopy.key.toggle(autopy.key.K_ALT, False)
            autopy.key.type_string(selection)
            #autopy.key.tap(autopy.key.K_ESCAPE)
            #autopy.key.toggle(autopy.key.K_ALT, False)
            autopy.key.tap(TAB_KEY, autopy.key.MOD_SHIFT)
            autopy.key.tap('v', autopy.key.MOD_CONTROL)
            autopy.key.tap('a', autopy.key.MOD_CONTROL)
            
        
    else: # not selection
        app.ExecuteCommand(command_name)
        
        
def cute_query_replace(editor=wingapi.kArgEditor,
                       app=wingapi.kArgApplication):
    '''
    Improved version of `query-replace` for finding and replacing in document.
    
    If text is selected, it will be used as the text to search for, and the
    contents of the clipboard will be offered as the replace value.
    
    Suggested key combination: `Alt-Comma`
    '''
    return _cute_general_replace('query-replace', editor=editor, app=app)


def cute_replace_string(editor=wingapi.kArgEditor,
                       app=wingapi.kArgApplication):
    '''
    Improved version of `replace-string` for finding and replacing in document.
    
    If text is selected, it will be used as the text to search for, and the
    contents of the clipboard will be offered as the replace value.
    
    Suggested key combination: `Alt-Period`
    '''    
    return _cute_general_replace('replace-string', editor=editor, app=app)