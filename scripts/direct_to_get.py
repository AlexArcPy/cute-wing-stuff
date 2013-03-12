# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

'''
This module defines the `direct_to_get` script.

See its documentation for more information.
'''


from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import re
import inspect

import wingapi

import shared


#caret_token = 'mUwMzJiNDg3MGE4NGE0ZmFjZGJkMGQ2NTNlNGQ4ZjQ5YTZjMGI1YzYwMmY0YjUw'

pattern = re.compile(
    r'''.*?(?P<square_brackets>\[(?P<key>.*?)\])$'''
)

def dict_direct_to_get(editor=wingapi.kArgEditor):
    '''
    Suggested key combination: Insert Ctrl-G
    '''
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    assert isinstance(document, wingapi.CAPIDocument)
    
    _, current_position = editor.GetSelection()
    current_line_number = document.GetLineNumberFromPosition(current_position)
    line_start = document.GetLineStart(current_line_number)
    line_end = document.GetLineEnd(current_line_number)
    line_head = document.GetCharRange(line_start, current_position)
    line_tail = document.GetCharRange(current_position, line_end)
    
    if ']' not in line_tail:
        print('''']' not in line_tail''')
        return
    
    first_closing_bracket_position = line_tail.find(']') + len(line_head) + \
                                                                     line_start
    
    text_until_closing_bracket = document.GetCharRange(
        line_start,
        first_closing_bracket_position + 1
    )
    
    match = pattern.match(text_until_closing_bracket)
    if not match:
        print('''no match''')
        print('{{{%s}}}' % text_until_closing_bracket)
        return
    else: # we have a match
        print(match.group('key'))
        print(match.group('square_brackets'))
    
    #with shared.UndoableAction(document):
        #start, end = shared.select_current_word(editor)    
        #variable_name = document.GetCharRange(start, end)
        #result_string = 'self.%s = %s' % (variable_name, variable_name)
        #document.DeleteChars(start, end - 1)
        #document.InsertChars(start, result_string)
        #editor.SetSelection(start + len(result_string),
                            #start + len(result_string))
        #editor.ExecuteCommand('new-line')
    
        
