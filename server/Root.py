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


from string import Template
from rf2db.utils import urlutil
from cherrypy.lib.static import serve_file

from server.config import Rf2Entries
from auth.ihtsdoauth import *

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))

refEntries = Rf2Entries.settings
poss_formats = [
    ('html','HTML'),
    ('xml', 'XML'),
    ('tsv', 'Tab Sep'),
    ('bsv', 'Bar Sep'),
    ('ditatable', 'Dita Table'),
    ('cntable', 'CollabNet Table'),
    ('json','JSON'),
    ]

formats_tmpl=Template('<td><a href="$root/$path?format=$fmt$sep$args"><button>$fmtlabel</button></a></td>')

def formats(path=None,args=""):
    root = urlutil.base_uri()
    sep = '&' if args else ''
    fmts = Template(formats_tmpl.safe_substitute(locals()))
    return '\t\n'.join(fmts.safe_substitute(locals()) for (fmt, fmtlabel) in poss_formats)


fcn_tmpl=Template("""<td>$label</td>
                <td><a href="$base_fcn">$fcn_desc</a></td>
                $fmts_sig
                <td>$fcn_sig</td>""")
def row(path, args, label='',base_fcn='',fcn_desc='',fcn_sig=''):
    fmts_sig = formats(path, args)
    return fcn_tmpl.safe_substitute(locals())


class Root(object):

    _cp_config = {
        'tools.sessions.on': True,
        'tools.auth.on' : True,
        'tools.auth_basic.on': False,
        'tools.auth_basic.realm' : 'rf2',
        'tools.auth_basic.checkpassword': False
    }

    @cherrypy.expose
    def index(self):
        return self.default('html','rf2.html')

    @cherrypy.expose
    def default(self, *kwargs):
        return ''.join(list(serve_file(os.path.join(_curdir,'..','static', *kwargs)))) % dict({'href_root':urlutil.href_settings.root}, **(refEntries.asdict()))



