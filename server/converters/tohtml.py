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
from rf2db.db.RF2LanguageFile import LanguageDB
from rf2db.db.RF2DescriptionFile import DescriptionDB

ldb = LanguageDB()
ddb = DescriptionDB()

doc_template = """<!DOCTYPE html>
<html>
<style type="text/css">

    thead {
        text-align: center;
        color: darkblue;
        border-width: 1px;
        padding: 1px;
        border-style: solid;
        border-color: gray;
        background-color: lightgrey;
    }

 </style>
<head>
    <title>%(title)s</title>
</head>
<body>
<table border="1">
    <thead>
    <tr>
        %(headings)s
    </tr>
    </thead>
    <tbody>
        %(body)s
    </tbody>
</table>

</body>
</html>"""

count_template = """<!DOCTYPE html>
<html>
<style type="text/css">

    thead {
        text-align: center;
        color: darkblue;
        border-width: 1px;
        padding: 1px;
        border-style: solid;
        border-color: gray;
        background-color: lightgrey;
    }

 </style>
<head>
    <title>RF2 Item Count</title>
</head>
<body>
<h2>Number of matching items: %s</h2>
</body>
</html>"""

td = """<td>%s</td>"""
row = """<tr>%s</tr>"""
a = """<span title='%s'><a href="/rf2/concept/%s/prefdescription">%s</a></span>"""

def as_html(parser_object, **_):
    def _pnFor(cid_or_did):
        cid_pn_did = ldb.preferred_term_for_concepts(cid_or_did)
        if cid_pn_did:
            return cid_pn_did[cid_or_did][0]
        pn = ddb.getDescriptionById_p(cid_or_did)
        return pn.term if pn else ''



    """
    @param parser_object:
    @return: tab separated value list of parser_object
    """
    def a_link(arg):
        return a % (_pnFor(arg[1]), arg[1], arg[1]) if arg[0] else arg[1]

    def td_row(items):
        return '\t\n'.join(td % a_link(e) for e in items)

    title = "RF2 Entry"
    (hdrRow, entryRows) = normalize(parser_object)
    if not (hdrRow or entryRows):
        try:
            return count_template % parser_object.numEntries, "text/html"
        except:
            return "Unknown object type - cannot format", 'text/plain'
    headings = td_row( (False, e) for e in hdrRow._fieldNames)
    body = '\t\n'.join(row % (td_row( (e.issctid(fn), e.strify(fn)) for fn in e._fieldNames)) for e in entryRows)
    return doc_template % locals(), 'text/html;charset=UTF-8'
