from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import inspect

import wingapi

import shared


def _decapitalize(string):
    if not string:
        return string
    return string[0].lower() + string[1:]


def _get_indent_size_in_pos(editor, pos):
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    assert isinstance(document, wingapi.CAPIDocument)
    
    with shared.SelectionRestorer(editor):
        line_number = document.GetLineNumberFromPosition(pos)
        line_start_pos = document.GetLineStart(line_number)
        editor.SetSelection(pos, pos)
        editor.ExecuteCommand('indent-to-match')
        line_text_start_pos = editor.GetSelection()[0]
        
        return line_text_start_pos - line_start_pos
    


def comment_braces(title):
    editor = wingapi.gApplication.GetActiveEditor()
    assert isinstance(title, basestring)
    assert isinstance(editor, wingapi.CAPIEditor)
    print(type(editor), editor)
    document = editor.GetDocument()
    assert isinstance(document, wingapi.CAPIDocument)
    with shared.UndoableAction(document):
        
        original_start, original_end = editor.GetSelection()
        original_end_line_number = \
                document.GetLineNumberFromPosition(original_end)
        original_document_length = document.GetLength()
        original_line_count = document.GetLineCount()
        
        indent_size = _get_indent_size_in_pos(editor, original_start)
        
        if title:
            raw_start_title = (' %s: ' % title.capitalize())
            raw_end_title = (' Finished %s. ' % _decapitalize(title))
        else:
            assert title == ''
            raw_start_title = ''
            raw_end_title = ''
            
        start_title_head = (' ' * indent_size) + '###' + raw_start_title
        end_title_head = (' ' * indent_size) + '###' + raw_end_title
        
        start_title = \
            start_title_head + '#' * (79 - len(start_title_head)) + '\n'
        end_title = \
            end_title_head + '#' * (79 - len(end_title_head)) + '\n'        
        tips_string = \
            (' ' * indent_size) + '#' + (' ' * (79 - indent_size - 2)) + '#\n'
        
        start_line_number = document.GetLineNumberFromPosition(original_start)
        start_line_first_char = document.GetLineStart(start_line_number)
        document.InsertChars(start_line_first_char, start_title + tips_string)
        
        end_line_number = original_end_line_number + \
            (document.GetLineCount() - original_line_count) + 1
        end_line_first_char = document.GetLineStart(end_line_number)
        document.InsertChars(end_line_first_char, tips_string + end_title)
    
        
