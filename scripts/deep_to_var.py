# Copyright 2009-2012 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `deep_to_var` script.

See its documentation for more information.
'''


from __future__ import with_statement

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import re

import wingapi

import shared


### Defining `getter_pattern`: ################################################
#                                                                             #
getter_verbs = ('get', 'calculate', 'identify', 'fetch', 'make', 'create',
                'grant', 'open')

getter_verb = '(?:%s)' % (
    '|'.join(
        '[%s%s]%s' % (verb[0], verb[0].upper(), verb[1:]) for verb in
        getter_verbs
    )
)

getter_pattern = re.compile(r'%s_?([a-zA-Z_][0-9a-zA-Z_]*)\(.*\)$' %
                                                                   getter_verb)
#                                                                             #
### Finished defining `getter_pattern`. #######################################


attribute_pattern = re.compile(r'\.([a-zA-Z_][0-9a-zA-Z_]*)$')
getitem_pattern = re.compile(r'''\[['"]([a-zA-Z_][0-9a-zA-Z_]*)['"]\]$''')

django_orm_get_pattern = re.compile(r'([a-zA-Z_][0-9a-zA-Z_]*)'
                                    r'\.objects\.get\(.*\)$')

patterns = [getter_pattern, attribute_pattern, getitem_pattern,
            django_orm_get_pattern]



def deep_to_var(editor=wingapi.kArgEditor):
    '''
    Create a variable from a deep expression.
    
    When you're programming, you're often writing lines like these:
    
        html_color = self._style_handler.html_color
        
    Or:
    
        location = context_data['location']
        
    Or:
        
        event_handler = super(Foobsnicator, self).get_event_handler()
    
    Or:
        
        user_profile = models.UserProfile.objects.get(pk=pk)
        
    What's common to all these lines is that you're accessing some expression,
    sometimes a deep one, and then getting an object, and making a variable for
    that object with the same name that it has in the deep expression.
    
    What this `deep-to-var` script will do for you is save you from having to
    write the `html_color = ` part, which is annoying to type because you don't
    have autocompletion for it.
    
    Just write your deep expression, like `self._style_handler.html_color`,
    invoke this `deep-to-var` script, and you'll get the full line and have the
    caret put on the next line.
    '''
    assert isinstance(editor, wingapi.CAPIEditor)
    document = editor.GetDocument()
    assert isinstance(document, wingapi.CAPIDocument)
    
    position, _ = editor.GetSelection()
    line_number = document.GetLineNumberFromPosition(position)
    line_start = document.GetLineStart(line_number)
    line_end = document.GetLineEnd(line_number)
    line = document.GetCharRange(line_start, line_end)
    line_stripped = line.strip()
    
    variable_name = None
    match = None
    for pattern in patterns:
        match = pattern.search(line_stripped)
        if match:
            (variable_name,) = match.groups()
            break
        
    if match:
        if variable_name != variable_name.lower():
            # `variable_name` has an uppercase letter, and thus is probably
            # camel-case. Let's flip it to underscore:
            variable_name = shared.camel_case_to_lower_case(variable_name)
        string_to_insert = '%s = ' % variable_name
        actual_line_start = line_start + \
                    shared.get_n_identical_edge_characters(line, character=' ')
        
        with shared.UndoableAction(document):
            
            document.InsertChars(actual_line_start, string_to_insert)
            new_position = line_end + len(string_to_insert)
            editor.SetSelection(new_position, new_position)
            editor.ExecuteCommand('new-line')