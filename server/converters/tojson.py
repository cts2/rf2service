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
import socket
from server.converters.toxml import as_xml
from server.config import ServiceSettings
from py4j.java_gateway import JavaGateway, GatewayClient, Py4JError, Py4JNetworkError


def as_json(rval, ns=None, **kwargs):
    """ Convert an XML rendering to JSON using an external py4j xml to josn conversion package """
    rval, mimetype = as_xml(rval,ns,**kwargs)
    if mimetype.startswith('application/xml;'):
        if not converter_link:
            newConverter()
        if not converter_link:
            raise cherrypy.HTTPError(503, "XML to JSON converter is unavailable")
        try:
            rval = converter_link.toJson(rval)
            mimetype = 'application/json;charset=UTF-8'
        except Py4JError:
            newConverter()
            rval = converter_link.toJson(rval)
            mimetype = 'application/json;charset=UTF-8'
    return rval, mimetype

converter_link = None
def newConverter():
    global converter_link
    print "Starting Java gateway on port: %s" % ServiceSettings.settings.gatewayport
    try:
        converter_link = JavaGateway(GatewayClient(port=int(ServiceSettings.settings.gatewayport))).jvm.org.json.XMLToJson()
    except socket.error as e:
        print e
        converter_link = None
    except Py4JNetworkError as e:
        print e

newConverter()
