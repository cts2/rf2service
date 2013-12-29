# -*- coding: utf-8 -*-
# Copyright (c) 2013, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


""" Convert a return value to a tab separated list.  This conversion is dependent on
the RF2 parsers package, where basic types have C{_fieldnames} which name the fields in the output and
iterator types have entries.
"""
def as_tsv(parser_object, **_):
    """
    @param parser_object:
    @return: tab separated value list of parser_object
    """
    (hdrRow, entryRows) = normalize(parser_object)
    if not (hdrRow or entryRows):
        try:
            return "Number of matching items: %s" % parser_object.numEntries, "text/plain"
        except:
            return "Unknown object type - cannot format", 'text/plain'


    hdrs = '\t'.join(hdrRow._fieldNames) if hdrRow else ''
    bodys = '\n'.join(['\t'.join([e.strify(fn) for fn in e._fieldNames]) for e in entryRows])
    return hdrs + '\n' + bodys, 'text/plain;charset=UTF-8'

def normalize(parser_object):
    """ Split the return into a header row and a list of entries
    @param rval:
    @return:
    """
    if hasattr(parser_object, '_fieldNames'):
        return parser_object, [parser_object]
    elif hasattr(parser_object, 'entry') and len(parser_object.entry):
        return parser_object.entry[0], parser_object.entry
    else:
        return None, []