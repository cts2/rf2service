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
from server.converters.totsv import as_tsv
from server.converters.toditatable import as_dita_table
from server.converters.tocollabnet import as_collabnet_table
from server.converters.tobsv import as_bsv
from server.converters.tohtml import as_html
from rf2db.db.RF2ModuleVersionsFile import ModuleVersionsDB


def loadmodules():
    global_rf2_parms_tmpl = """
    <p>
        <label><b>Include inactive records: </b><input type="radio" name="active" value="False"/></label><br/>
        <br/><b>Restrict to module id(s):</b>
        %(modulelist)s
    </p>"""
    moduleentry_tmpl = """<input type="checkbox" name="moduleid" value=%s>%s</input>"""
    modulelist = '\t\t\n'.join(moduleentry_tmpl % (e[0],e[1]) for e in map(lambda rec: rec.split('\t'),
                                                                           ModuleVersionsDB().getModulesids()))
    return global_rf2_parms_tmpl % locals()

global_rf2_parms = loadmodules()

global_iter_parms = """<p>
<b>Start on page:</b><input type="number" size=3 name="page"/>
<b> Maximum to return</b> (0 means return a count):<input type="number" size=4 name="maxtoreturn"/>
</p>"""

class RF2BaseNode(BaseNode):
    extensions = ["<br/>",
                  """<p><b>Format:</b><input type="radio" name="format" value="xml">XML</input>
<input type="radio" name="format" value="tsv">TSV</input>
<input type="radio" name="format" value="ditatable">DITA</input>
<input type="radio" name="format" value="cntable">CollabNet</input>
<input type="radio" name="format" value="json">JSON</input>
<input type="radio" name="format" value="html" checked="True">HTML</input></p>""",
                  global_rf2_parms]
    namespace = rf2.Namespace
    formats = {'tsv':as_tsv,
               'ditatable':as_dita_table,
               'cntable':as_collabnet_table,
               'bsv':as_bsv,
               'html':as_html}


        