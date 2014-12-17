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

from server.config import ServiceSettings
from rf2db.utils.xmlutils import prettyxml, cleanxml

xml_value_template = """<?xml version="1.0" encoding="UTF-8"?>
<val>%s</val>"""
xml_mime_type = 'application/xml;charset=UTF-8'


def as_xml(rval, ns=None, **kwargs):
    """ Convert a pyxb object into xml, otherwise return a simple xml representation with a value field
    @param rval: pyxb or string object
    @param ns: namespace to use for object in place of default
    @param kwargs: if 'xslt' in the objects, add it to the return value
    @return: tuple - xml or string rendering, mime type if xml else None
    """
    if 'toxml' in [method for method in dir(rval) if callable(getattr(rval, method))]:
        xslt = kwargs.pop('xslt', None)
        if xslt:
            xsltPath = ServiceSettings.settings.staticroot + "xsl/%s.xsl" % xslt
            xslt = '\n<?xml-stylesheet type="text/xsl" href="%s"?>' % xsltPath
        return prettyxml(rval, ns=ns, xslt=xslt, validate=True), 'application/xml;charset=UTF-8'
    elif str(rval).startswith('<?xml version="1.0"'):
        return str(rval), xml_mime_type
    return xml_value_template % cleanxml(rval), xml_mime_type