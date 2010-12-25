from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))


import wingapi

import shared


def flip_case(editor=wingapi.kArgEditor):
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    assert isinstance(document, wingapi.CAPIDocument)
    with shared.UndoableAction(document):
        start, end = shared.select_current_word(editor)
        word = document.GetCharRange(start, end)
        
        is_lower_case = word.islower()
        is_camel_case = not is_lower_case 
        
        if is_lower_case:
            new_word = shared.lower_case_to_camel_case(word)
        
        else:
            assert is_camel_case
            new_word = shared.camel_case_to_lower_case(word)        
        
        document.DeleteChars(start, end-1)
        document.InsertChars(start, new_word)
        editor.SetSelection(start + len(new_word),
                            start + len(new_word))
        #editor.ExecuteCommand('new-line')
    
        
