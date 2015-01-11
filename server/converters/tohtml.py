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
import html

from server.converters.normalize import normalize
from server.config import ServiceSettings
from rf2db.db.RF2LanguageFile import LanguageDB
from rf2db.db.RF2DescriptionFile import DescriptionDB
from rf2db.schema.rf2 import Iterator
from rf2db.utils import urlutil
from rf2db.utils.sctid import sctid
from rf2db.parameterparser.ParmParser import uuidparam

ldb = LanguageDB()
ddb = DescriptionDB()

cont_template = """<div class="tcount">%s entries returned</div>"""
next_template = """<a href="%s"><button>Next Page</button></a>"""
prev_template = """<a href="%s"><button>Prev Page</button></a>"""""


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
%(continuation)s
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

basic_template = """<!DOCTYPE html>
<html>
<head>
    <title>Basic Return</title>
</head>
<body>
<pre>%s</pre>
</body>
</html>"""

td = """<td>%s</td>"""
row = """<tr>%s</tr>"""
ca = "<span title='%(pn)s'><a href='%(rf2root)sconcept/%(cid)s/prefdescription'>%(cid)s</a></span>"
da = "<span title='%(pn)s'><a href='%(rf2root)sdescription/%(cid)s'>%(cid)s</a></span>"
cts2a = "<span title='%(pn)s'><a href='%(cts2root)sentity/%(cid)s?format=html'>%(cid)s</a></span"
refseta = "<a href='%(rf2root)srefset/%(rsid)s?format=html'>%(rsid)s</a>"

def addsep(link):
    return link + '/' if not link.endswith('/') else link

def as_html(parser_object, **_):
    def _pnFor(cid_or_did):
        """ Return the preferred name for a concept id or the term for a description id
        @param cid_or_did: concept or description id
        @return: tuple(name, type) where type is 'c' or 'd'
        """
        cid_pn_did = ldb.preferred_term_for_concepts(cid_or_did)
        if cid_pn_did:
            return (cid_pn_did[cid_or_did][0], 'c')
        pn = ddb.read(cid_or_did)
        return (pn.term, 'd') if pn else ('', '')



    """
    @param parser_object:
    @return: tab separated value list of parser_object
    """
    def a_link(arg):
        if arg[0] and sctid.isValid(arg[1]):
            (pn, pt) = _pnFor(arg[1])
            cid = arg[1]
            cts2root = addsep(ServiceSettings.settings.cts2base)
            rf2root = addsep(urlutil.base_uri())
            if pt:
                return (cts2a if arg[2] == 'conceptId' else ca if pt=='c' else da) % locals()
        elif uuidparam()._isValid(arg[1]):
            rf2root = addsep(urlutil.base_uri())
            rsid = arg[1]
            return refseta % locals()
        return arg[1]

    def td_row(items):
        try:
            return '\t\n'.join(td % a_link(e) for e in items)
        except UnicodeDecodeError:
            return '\t\n'.join(td % a_link(e).encode('utf-8') for e in items)

    title = "RF2 Entry"
    (hdrRow, entryRows) = normalize(parser_object)
    if not (hdrRow or entryRows):
        try:
            return count_template % parser_object.numEntries, "text/html"
        except:
            try:
                return basic_template % html.XHTML(text=parser_object), "text/html"
            except:
                return parser_object, 'text/plain'
    headings = td_row((False, e, e) for e in hdrRow._fieldNames)
    body = '\t\n'.join(row % (td_row((e.issctid(fn), e.strify(fn), fn) for fn in e._fieldNames)) for e in entryRows)
    continuation = ''
    if isinstance(parser_object, Iterator):
        continuation += cont_template % parser_object.numEntries
        if parser_object.next:
            continuation += next_template % parser_object.next
        if parser_object.prev:
            continuation += prev_template % parser_object.prev


    return doc_template % locals(), 'text/html;charset=UTF-8'
