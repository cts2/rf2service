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
from server.BaseNode import BaseNode
from rf2db.schema import rf2

tableTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<table>
   <tgroup cols="%s">
      <thead>
         <row>
             %s
         </row>
      </thead>
      <tbody>
        %s
      </tbody>
   </tgroup>
</table>"""

entryTemplate="<entry>%s</entry>"

def normalize(rval):
    if hasattr(rval, '_fieldNames'):
        return rval, [rval]
    elif hasattr(rval, 'entry') and len(rval.entry):
        return rval.entry[0], rval.entry
    else:
        return None, []




def toTsv(rval, **_):
    """ Tab separated value return format """
    (hdrRow, entryRows) = normalize(rval)
    
    hdrs = '\t'.join(hdrRow._fieldNames) if hdrRow else ''
    bodys = '\n'.join(['\t'.join([e.strify(fn) for fn in e._fieldNames]) for e in entryRows])
    return hdrs + '\n' + bodys, 'text/plain;charset=UTF-8'

def ditaTable(rval, **_):
    (hdrRow, entryRows) = normalize(rval)
    cols = len(hdrRow._fieldNames) if hdrRow else 0

    hdrs = '\n'.join([entryTemplate % fn for fn in hdrRow._fieldNames]) if hdrRow else ''
    bodys = ''.join(['<row>\n' + '\n'.join([entryTemplate % e.strify(fn) for fn in e._fieldNames]) + '</row>\n' for e in entryRows])
    return tableTemplate % (cols, hdrs, bodys),'application/xml;charset=UTF-8'

def collabNetTable(rval, **_):
    (hdrRow, entryRows) = normalize(rval)
    
    hdrs = ' || '.join(hdrRow._fieldNames) if hdrRow else ''
    bodys = '\n| '.join([' | '.join([e.strify(fn) for fn in e._fieldNames]) for e in entryRows])
    return '|| ' + hdrs + '\n| ' + bodys, 'text/plain;charset=UTF-8'

def pythonString(rval, **_):
    (_, entryRows) = normalize(rval)
    return '\t"' + '"\n\t"'.join(['|'.join([e.strify(fn) for fn in e._fieldNames]) for e in entryRows]) + '"'

class RF2BaseNode(BaseNode):
    extension = """<p><b>Format:</b><input type="radio" name="format" value="xml" checked="True">XML</input>
<input type="radio" name="format" value="tsv">TSV</input>
<input type="radio" name="format" value="ditatable">DITA</input>
<input type="radio" name="format" value="cntable">CollabNet</input>
<input type="radio" name="format" value="json">JSON</input></p>"""
    namespace = rf2.Namespace
    formats = {'tsv':toTsv,
               'ditatable':ditaTable,
               'cntable':collabNetTable}


        