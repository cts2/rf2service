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
import cherrypy
from rf2db.utils import urlutil
from rf2db.db.RF2DBConnection import config, dbconfig

html = """<!DOCTYPE html>
<html>
<head>
    <title>RF2 Server Configuration</title>
</head>
<body>
<h1>Database Configuration</h1>
<table border="1">
    <tr>
        <td>Host</td>
        <td>%(host)s
    </tr>
    <tr>
        <td>Port</td>
        <td>%(port)s</td>
    </tr>
    <tr>
        <td>DB</td>
        <td>%(db)s</td>
    </tr>
    <tr>
        <td>Charset</td>
        <td>%(charset)s</td>
    </tr>
</table>
<h1>URL Settings</h1>
<table border="1">
    <tr>
        <td>Host</td>
        <td>%(href_host)s</td>
    </tr>
        <tr>
        <td>Root</td>
        <td>%(href_root)s</td>
    </tr>
    <tr>
        <td>Relative URI</td>
        <td>%(reluri)s</td>
    </tr>
    <tr>
        <td>Base URI</td>
        <td>%(baseuri)s</td>
    </tr>
    <tr>
        <td>Complete URI</td>
        <td>%(completeuri)s</td>
    </tr>
</table>

</body>
</html>"""

# config_parms = ConfigArgs('dbparms',
#                           [ConfigArg('host', help='MySQL DB Host', default='localhost'),
#                            ConfigArg('port', help='MySQL DB Port'),
#                            ConfigArg('user', abbrev='u', help='MySQL User Id'),
#                            ConfigArg('passwd', abbrev='p', help='MySQL Password'),
#                            ConfigArg('db', abbrev='db', help='Database', default='rf2'),
#                            ConfigArg('charset', help='MySQL Character Set', default='utf8')
#                           ])
# config = ConfigManager(config_parms)
#
# debug_parms = ConfigArgs('debug',
#                          [ConfigArg('trace', help='Trace SQL Calls', action='store_true'),
#                           ConfigArg('nocache', help='Turn off cache for debugging', action='store_true')
#                          ])
# dbconfig = ConfigManager(debug_parms)



class ServerConf(object):

    @cherrypy.expose
    def default(self, *args, **kwargs):

        host = config.host
        port = config.port
        db = config.db
        charset = config.charset

        href_host = urlutil.href_settings.host
        href_root = urlutil.href_settings.root
        reluri = urlutil.relative_uri()
        baseuri = urlutil.base_uri()
        completeuri = urlutil.complete_uri()

        return html % vars()


