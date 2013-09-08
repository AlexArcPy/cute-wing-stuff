# Copyright 2009-2013 Ram Rachum.
# This program is distributed under the MIT license.

'''
This module defines the `forward_half_page` script.

See its documentation for more information.
'''

from __future__ import division
from __future__ import with_statement

import os.path, sys
sys.path += [
    os.path.dirname(__file__), 
    os.path.join(os.path.dirname(__file__), 'third_party.zip'), 
]


import wingapi

import shared

    
def forward_half_page(editor=wingapi.kArgEditor):
    '''
    Move half a page down.
    
    This is essentially one half of Page-Down.

    Suggested key combination: `Alt-Page_down` (As long as you don't use Wing's
    folding.)
    '''
    shared._move_half_page(1, editor=editor)
    