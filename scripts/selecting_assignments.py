# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

'''
This module defines scripts for selecting parts of assignments.

See its documentation for more information.
'''

from __future__ import with_statement

import re
import _ast

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import wingapi

import shared


SAFETY_LIMIT = 60
'''The maximum number of times we'll do `select-more` before giving up.'''

def _ast_parse(string):
    return compile(string, '<unknown>', 'exec', _ast.PyCF_ONLY_AST)
    

def _is_expression(string):
    '''Is `string` a Python expression?'''
    
    # Throwing out '\r' characters because `ast` can't process them for some
    # reason:
    string = string.replace('\r', '')
    try:
        nodes = _ast_parse(string).body
    except SyntaxError:
        return False
    else:
        if len(nodes) != 1:
            return False
        else:
            (node,) = nodes
            return type(node) == _ast.Expr
    


variable_name_pattern_text = r'[a-zA-Z_][0-9a-zA-Z_]*'
dotted_name_pattern = re.compile(
    r'\.?^%s(\.%s)*$' %
                       (variable_name_pattern_text, variable_name_pattern_text)
)

def _is_dotted_name(string):
    '''Is `string` a dotted name?'''
    assert isinstance(string, str)
    return bool(dotted_name_pattern.match(string.strip()))
    

whitespace_characters = ' \n\r\t\f\v'
    
def _is_whitespaceless_name(string):
    '''Is `string` a whitespace-less name?'''
    assert isinstance(string, str)
    return not any((whitespace_character in string for whitespace_character
                in whitespace_characters))
    

def _select_more_until_biggest_match(condition, editor=wingapi.kArgEditor):
    '''`select-more` until reaching biggest text that satisfies `condition`.'''
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    select_more = lambda: wingapi.gApplication.ExecuteCommand('select-more')
    is_selection_good = lambda: condition(
        document.GetCharRange(*editor.GetSelection()).strip()
    )

    last_success_n_iterations = None
    
    last_start, last_end = original_selection = editor.GetSelection()
    
    with shared.ScrollRestorer(editor):
        with shared.SelectionRestorer(editor):
            for i in range(SAFETY_LIMIT):
                select_more()
                current_start, current_end = editor.GetSelection()
                if (current_start == last_start) and (current_end == last_end):
                    break
                if is_selection_good():
                    last_success_n_iterations = i
                last_start, last_end = current_start, current_end
                
        if last_success_n_iterations is not None:
            for i in range(last_success_n_iterations+1):
                select_more()
            
            
def select_expression(editor=wingapi.kArgEditor):
    '''
    Select the Python expression that the cursor is currently on.
    
    This does `select-more` until the biggest possible legal Python expression
    is selected.

    Suggested key combination: `Ctrl-Alt-Plus`
    '''
    _select_more_until_biggest_match(_is_expression, editor)
            
    
def select_dotted_name(editor=wingapi.kArgEditor):
    '''
    Select the dotted name that the cursor is currently on, like `foo.bar.baz`.
    
    This does `select-more` until the biggest possible dotted name is selected.
    
    Suggested key combination: `Alt-Plus`
    '''
    _select_more_until_biggest_match(_is_dotted_name, editor)
    
    
def select_whitespaceless_name(editor=wingapi.kArgEditor):
    '''
    Select the whitespace-less name that the cursor is currently on.
    
    Example: `foo.bar.baz(e=3)`.
    
    This does `select-more` until the biggest possible whitespace-less name is
    selected.
    
    Suggested key combination: `Ctrl-Alt-Equal`
    '''
    _select_more_until_biggest_match(_is_whitespaceless_name, editor)
    

_scope_name_regex = re.compile(
    r'''^(.*?(?:(?:def )|(?:class )))([a-zA-Z_][0-9a-zA-Z_]*)''',
    flags=re.DOTALL
)

def select_scope_name(editor=wingapi.kArgEditor):
    '''
    Select the name of the function or class that the cursor is currently on.
    
    Suggested key combination: `Alt-Colon`
    '''
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    document_text = shared.get_text(document)
    with shared.SelectionRestorer(editor):    
        editor.ExecuteCommand('select-scope')
        scope_start, scope_end = editor.GetSelection()
        
    scope_contents = document_text[scope_start : scope_end]
    match = _scope_name_regex.match(scope_contents)
    if not match:
        return
    stuff_before_scope_name, scope_name = match.groups()
    scope_name_start = scope_start + len(stuff_before_scope_name)
    scope_name_end = scope_name_start + len(scope_name)
    assert document_text[scope_name_position :
                             scope_name_position+len(scope_name)] == scope_name
    
    with shared.UndoableAction(document):
        editor.SetSelection(scope_name_start, scope_name_end)
    
    
    
re.compile(
    r'''(?<=\n)(?P<indent>[ \t]*)''' # Before LHS
    r'''(?P<lhs>[A-Za-z_][A-Za-z0-9_]*)''' # LHS
    r''' *(?:[+\-*/%|&^]|<<|>>|//|\*\*)?= *''' # operator and padding
    # RHS:
    r'''(?P<rhs>[^ ][^\n]*\n''' 
    r'''(?:(?:[ \t]*[)\]}][^\n]*[\n])|(?:(?=(?P=indent)[ \t])[^\n]*\n))*)''', 
    flags=re.DOTALL
)    
    
    

def select_next_lhs():
    pass

def select_prev_lhs():
    pass

def select_next_rhs():
    pass

def select_prev_rhs():
    pass
    
    