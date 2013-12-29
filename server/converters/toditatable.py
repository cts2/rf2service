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

from server.converters.totsv import normalize

entryTemplate="<entry>%s</entry>"
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

def as_dita_table(parser_object, **_):
    (hdrRow, entryRows) = normalize(parser_object)
    if not (hdrRow or entryRows):
        try:
            return "Number of matching items: %s" % parser_object.numEntries, "text/plain"
        except:
            return "Unknown object type - cannot format", 'text/plain'

    cols = len(hdrRow._fieldNames) if hdrRow else 0

    hdrs = '\n'.join([entryTemplate % fn for fn in hdrRow._fieldNames]) if hdrRow else ''
    bodys = ''.join(['<row>\n' + '\n'.join([entryTemplate % e.strify(fn) for fn in e._fieldNames]) + '</row>\n' for e in entryRows])
    return tableTemplate % (cols, hdrs, bodys),'application/xml;charset=UTF-8'