# Copyright 2009-2014 Ram Rachum.
# This program is distributed under the MIT license.

from __future__ import with_statement

import os.path, sys
sys.path += [
    os.path.dirname(__file__), 
    os.path.join(os.path.dirname(__file__), 'third_party.zip'), 
]

import ast
import re
import collections

import wingapi
import wingutils.datatype
import guiutils.formbuilder
import guiutils.wgtk
import guiutils.dialogs

import shared
import string_selecting


string_head_pattern = re.compile('''^(?P<modifiers>(?:b|u|)r?)'''
                                 '''(?P<quote>\'(?:\'\')?|\"(?:\"\")?)''',
                                 re.I)

base_escape_map = {
    '\\': '\\\\',
    '\'': '\\\'',
    '\"': '\\\"',
    '\a': '\\a',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
    '\v': '\\v',
}


def format_string(string, double=False, triple=False,
                  bytes_=False, raw=False, unicode_=False):
    assert bytes_ + unicode_ in (0, 1)
    quote_string = ('"' if double else "'") * (3 if triple else 1)
    
    content_list = []
        
    i = 0
    while i < len(string):
        if triple and string.startswith(quote_string, i):
            content_list.append('\\%s' % quote_string)
            i += 3
            continue
        elif triple and (i == len(string) - 1) and string[i] == quote_string[0]:
            content_list.append('\\%s' % quote_string[0])
            i += 1
            continue # Will now end loop because we're at end of string
        else:
            current_substring = string[i]
            i += 1

        if ((current_substring in ('"', "'")) and triple) or \
                                 (current_substring == '"' and not double) or \
                                         (current_substring == "'" and double):
            content_list.append(current_substring)
        elif current_substring in base_escape_map:
            content_list.append(base_escape_map[current_substring])
        else:
            content_list.append(current_substring)
            
    content = ''.join(content_list)
    
    formatted_string = '%s%s%s%s' % (
        ''.join((
            ('b' if bytes_ else ''),
            ('u' if unicode_ else ''),
            ('r' if raw else ''),
        )),
        quote_string,
        content,
        quote_string
    )
    #if isinstance(formatted_string, unicode):
        #formatted_string = formatted_string.encode()
    if not ast.literal_eval(formatted_string) == string:
        raise Exception('Formatting unsuccessful: @%s@  |||  @%s@  ||| @%s@'
              % (string, ast.literal_eval(formatted_string), formatted_string))
    return formatted_string
    

def _bool_to_qt_check_state(bool_):
    return guiutils.wgtk.Qt.Checked if bool_ else guiutils.wgtk.Qt.Unchecked

# def shit_print(s):
    # open('c:\\tits.txt', 'a').write(s)
    

def enter_string():
    app = wingapi.gApplication


    editor = app.GetActiveEditor()
    document = editor.GetDocument()
    selection_start, selection_end = editor.GetSelection()
    
    widget = guiutils.wgtk.QWidget()
    layout = guiutils.wgtk.QVBoxLayout()
    widget.setLayout(layout)
    text_edit_label = guiutils.wgtk.QLabel('&Text:')
    text_edit = guiutils.wgtk.QTextEdit()
    text_edit_label.setBuddy(text_edit)
    sub_layout = guiutils.wgtk.QHBoxLayout()
    bytes_checkbox = guiutils.wgtk.QCheckBox('&Bytes')
    unicode_checkbox = guiutils.wgtk.QCheckBox('&Unicode')
    raw_checkbox = guiutils.wgtk.QCheckBox('&Raw')
    double_checkbox = guiutils.wgtk.QCheckBox('&Double')
    triple_checkbox = guiutils.wgtk.QCheckBox('Tri&ple')
    for checkbox in (bytes_checkbox, unicode_checkbox, raw_checkbox,
                     double_checkbox, triple_checkbox):
        sub_layout.addWidget(checkbox)
    layout.addWidget(text_edit_label)
    layout.addWidget(text_edit)
    layout.addLayout(sub_layout)
    
    replacing_old_string = \
        string_selecting._is_position_on_strict_string(editor, selection_start)
    if replacing_old_string:
        old_string_start, old_string_end = \
           string_selecting._find_string_from_position(editor, selection_start)
        old_string_raw = document.GetCharRange(old_string_start, old_string_end)
        old_string = ast.literal_eval(old_string_raw)
        modifiers = string_head_pattern.match(old_string_raw). \
                                                     group('modifiers').lower()
        quote = string_head_pattern.match(old_string_raw).group('quote')
        bytes_checkbox.setCheckState(_bool_to_qt_check_state('b' in modifiers))
        unicode_checkbox.setCheckState(_bool_to_qt_check_state('u' in modifiers))
        raw_checkbox.setCheckState(_bool_to_qt_check_state('r' in modifiers))
        double_checkbox.setCheckState(_bool_to_qt_check_state('"' in quote))
        triple_checkbox.setCheckState(_bool_to_qt_check_state(len(quote) == 3))
        text_edit.setText(old_string)
        
    def ok():
        with shared.UndoableAction(document):
            # try:
            string = text_edit.toPlainText()
            bytes_ = bool(bytes_checkbox.checkState())
            unicode_ = bool(unicode_checkbox.checkState())
            raw = bool(raw_checkbox.checkState())
            double = bool(double_checkbox.checkState())
            triple = bool(triple_checkbox.checkState())
            formatted_string = format_string(string, bytes_=bytes_,
                                             unicode_=unicode_, raw=raw,
                                             double=double, triple=triple)
            if replacing_old_string:
                document.DeleteChars(old_string_start, old_string_end - 1)
                document.InsertChars(old_string_start, formatted_string)
                new_selection = old_string_start + len(formatted_string)
            else:
                document.DeleteChars(selection_start, selection_end-1)
                document.InsertChars(selection_start, formatted_string)
                new_selection = selection_start + len(formatted_string)
            editor.SetSelection(new_selection, new_selection)
            # except Exception as exception:
                # import traceback, sys
                # shit_print(
                    # ''.join(traceback.format_exception(*sys.exc_info()))
                # )
    buttons = [
        guiutils.dialogs.CButtonSpec('_OK', ok),
        guiutils.dialogs.CButtonSpec('_Cancel', None),
    ]
    dialog = guiutils.dialogs.CWidgetDialog(None, 'Edit string',
                                            'Edit string', widget, buttons)
    dialog.RunAsModal()    
    
    