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


from cherrypy        import request, config, HTTPRedirect
from urlparse        import urlsplit,parse_qs, urlunsplit
from urllib          import urlencode

from rf2db.utils     import xmlutils

dropParms = ['bypass']


def redirect(reluri):
    raise HTTPRedirect(baseURI() + '/' + reluri)

def baseURI():
    """ Return the base URI - up to the root of the service without an additional parameters
        that get you to the CTS2 service itself.  This is used to create URL's to ancillary
        files and support services.

        Must be accessed in the context of a cherrypy request
    """
    return request.base + request.app.script_name

def completeURISansParms():
    """ Return the complete URI of this call sans parms """
    return baseURI() + request.path_info

def completeURI():
    """ Return the complete URI that invoked this call """
    return stripControlParams(completeURISansParms() + ('?' + request.query_string) if request.query_string else '')

def forXML(uri):
    """ Escape XML nasties in a URI """
    return xmlutils.cleanxml(uri)

def relativeURI():
    """ Return the relative URI that invoked this call """
    return request.path_info[len(baseURI()):]

def stripControlParams(url):
    """ Remove any control parameters from a URL that should not be forwarded.
        This includes user ids, passwords and bypass parameters
    """
    spliturl = urlsplit(xmlutils.uncleanxml(url))
    urlparms = parse_qs(spliturl.query, True)
    for d in dropParms:
        urlparms.pop(d, None)
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    if '@' in splitlist[1]: splitlist[1] = splitlist[1].split('@')[1]
    return urlunsplit(splitlist)
      
def appendParams(baseURL,parms):
    """ Append a parameter to the base URI 
    @param baseURI: The uri to append the parameters to
    @type baseURI: c{URI}
    
    @param parms: the list of parameters to append
    @type parms: c{dict}
    """
    spliturl = urlsplit(baseURL)
    urlparms = parse_qs(spliturl.query,True)
    for (k,v) in parms.items():
        urlparms[k] = v
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    return urlunsplit(splitlist)

def removeParams(baseURL,parms):
    """ Remove parameter or parameters from the base URI
     @param baseURI: The uri to append the parameters to
    @type baseURI: c{URI}
    
    @param parms: the list of parameters to remove
    @type parms: c{list} or c{string}
    """
    if not isinstance(parms, (list, tuple)):
        parms = [parms]
    spliturl = urlsplit(baseURL)
    urlparms = parse_qs(spliturl.query,True)
    for k in parms:
        urlparms.pop(k, None)
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    return urlunsplit(splitlist)


