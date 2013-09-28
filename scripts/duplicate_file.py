# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

from __future__ import with_statement

import os.path
import shutil

import os.path, sys; sys.path.append(os.path.dirname(__file__))

import wingapi
import wingutils.datatype
import guiutils.formbuilder

import shared


def duplicate_file(new_file_name):
    
    app = wingapi.gApplication
    editor = app.GetActiveEditor()
    document = editor.GetDocument()
    original_file_path = document.GetFilename()
    folder, original_file_name = os.path.split(original_file_path)
    if '.' in original_file_name and '.' not in new_file_name:
        new_file_name += '.%s' % original_file_name.rsplit('.')[-1]
    new_file_path = os.path.join(folder, new_file_name)
    
    shutil.copy(original_file_path, new_file_path)
    
    app.OpenEditor(new_file_path)
    
    
    
duplicate_file.arginfo = lambda: \
    {
        'new_file_name': wingapi.CArgInfo(
            label='New file name (can omit extension)',
            type=wingutils.datatype.CType(''),
            formlet=guiutils.formbuilder.CSmallTextGui(
                default=os.path.split(
                    wingapi.gApplication.GetActiveEditor().GetDocument().
                                                                  GetFilename()
                )[-1],
                select_on_focus=True
            ),
            doc=''
            ),
    }

_no_reload_scripts = True