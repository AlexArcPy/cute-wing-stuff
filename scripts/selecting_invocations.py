# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

'''
This module defines scripts for selecting invocations.

See its documentation for more information.
'''

from __future__ import with_statement

import re
import bisect

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import wingapi

import shared

    
invocation_pattern = re.compile(r'''[A-Za-z_][A-Za-z_0-9]* *\(''')    
    

def get_span_of_opening_parenthesis(document, position):
    assert isinstance(document, wingapi.CAPIDocument)
    document_text = shared.get_text(document)
    if not document_text[position] == '(': raise Exception
    for i in range(1, len(document_text) - 1 - position):
        portion = document_text[position:position+i+1]
        if portion.count('(') == portion.count(')'):
            if not portion[-1] == ')': raise Exception
            return (position, position + i + 1)
    else:
        return (position, position)
        
    

def _get_matches(document):
    assert isinstance(document, wingapi.CAPIDocument)
    document_text = shared.get_text(document)
    return tuple(invocation_pattern.finditer(document_text))

def get_invocation_positions(document):
    matches = _get_matches(document)
    return tuple(match.span(1) for match in matches)
    
def get_argument_batch_positions(document):
    matches = _get_matches(document)
    parenthesis_starts = tuple(match.span(0)[1]-1 for match in matches)
    return map(
        lambda parenthesis_start:
                  get_span_of_opening_parenthesis(document, parenthesis_start),
        parenthesis_starts
    )
    
###############################################################################


def select_next_invocation(editor=wingapi.kArgEditor,
                           app=wingapi.kArgApplication):
    '''
    Select the next invocation of a callable, e.g `foo.bar(baz)`.
    
    Suggested key combination: `Ctrl-Alt-8`
    '''
    assert isinstance(editor, wingapi.CAPIEditor)
    _, position = editor.GetSelection()
    position += 1

    invocation_positions = get_invocation_positions(editor.GetDocument())
    invocation_ends = tuple(invocation_position[1] for invocation_position in
                            invocation_positions)
    invocation_index = bisect.bisect_left(invocation_ends, position)
    
    if 0 <= invocation_index < len(invocation_ends):
        app.ExecuteCommand('set-visit-history-anchor')
        editor.SetSelection(*invocation_positions[invocation_index])
        

def select_prev_invocation(editor=wingapi.kArgEditor,
                           app=wingapi.kArgApplication):
    '''
    Select the previous invocation of a callable, e.g `foo.bar(baz)`.
    
    Suggested key combination: `Ctrl-Alt-Asterisk`
    '''    
    assert isinstance(editor, wingapi.CAPIEditor)
    position, _ = editor.GetSelection()
    position -= 1

    invocation_positions = get_invocation_positions(editor.GetDocument())
    invocation_starts = tuple(invocation_position[0] for invocation_position
                              in invocation_positions)
    invocation_index = bisect.bisect_left(invocation_starts, position) - 1
    
    if 0 <= invocation_index < len(invocation_starts):
        app.ExecuteCommand('set-visit-history-anchor')
        editor.SetSelection(*invocation_positions[invocation_index])


###############################################################################

def select_next_argument(editor=wingapi.kArgEditor,
                         app=wingapi.kArgApplication):
    
    assert isinstance(editor, wingapi.CAPIEditor)
    _, position = editor.GetSelection()
    position += 1

    argument_batch_positions = get_argument_batch_positions(editor.GetDocument())
    argument_batch_ends = tuple(argument_batch_position[1] for argument_batch_position in
                            argument_batch_positions)
    argument_batch_index = bisect.bisect_left(argument_batch_ends, position)
    
    if 0 <= argument_batch_index < len(argument_batch_ends):
        app.ExecuteCommand('set-visit-history-anchor')
        editor.SetSelection(*argument_batch_positions[argument_batch_index])
        