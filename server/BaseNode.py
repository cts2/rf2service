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
import os
import socket
from lxml import etree


from rf2db.utils import listutils
from rf2db.utils.kwutil import kwget, best_match, preference_order
from server.utils import URLUtil, negotiateFormat
from server.converters.toxml import as_xml
from server.converters.tojson import as_json
from server.converters.tohtml import as_html

htmlHead = "<!DOCTYPE html>"

def expose(f, methods=None): #@ReservedAssignment
    """ Expose function - wrapper to manage arguments and control formatting into and out of web services """
    if not methods: methods = []

    @cherrypy.tools.allow(methods=methods+['GET','HEAD'])
    @cherrypy.expose
    def wrapped_f(self, *args, **kwargs):

        # Make a local image of the arguments for inside reference
        self._kwargs = kwargs.copy()
        if kwargs.get('_inside', False):
            # The innermost formatters trump the outer
            kwargs['_formats'] = dict(kwargs['_formats'].items(), self.formats.items())
            # As does the namespace
            if self.namespace:
                kwargs['_ns'][0] = self.namespace
            return f(self, *args, **kwargs)

        # Acquire the required return format information and strip the bypass information
        rtnfmt = kwargs.pop('format', None)

        kwargs.pop('bypass',None)
 
        kwargs['_formats'] = {'xml':  as_xml,
                              'json': as_json,
                              'html': as_html}.copy()
        kwargs['_ns'] = [None]
        if self.namespace:
            kwargs['_ns'][0] = self.namespace
        for (k,v) in self.formats.items():
            kwargs['_formats'][k] = v 
        kwargs['_inside']  = True
        
        # Function can return one of:
        # formatted string           - to be returned directly to the caller, unformatted
        # class                      - assumed to have a toxml() function
        # tuple                      - (rval, (error code, error message))
        #                               rval is string or class as above

        rtn = f(self, *args, **kwargs)
        
        rval, (err, msg) = rtn if isinstance(rtn, (list, tuple)) else (rtn, (500, 'Internal Server Error'))
        if not rval:
            raise cherrypy.HTTPError(err, msg)
        if str(rval).startswith(htmlHead):
            return rval
        if not rtnfmt:
            rtnfmt = negotiateFormat.negotiate_format(kwargs['_formats'].keys(), cherrypy.request.headers)
        rtnfmt = listutils.flatten(rtnfmt)
        if rtnfmt in kwargs['_formats']:
            ns = kwargs['_ns'][0] if kwargs['_ns'] else None
            (rval, enc) = kwargs['_formats'][rtnfmt](rval, ns=ns, **self._kwargs)
            cherrypy.response.headers['Content-type'] = enc if enc else 'text/plain;charset=UTF-8'
            return rval.encode('utf-8') if rtnfmt in('xml','html', 'json') else rval
        else:
            raise cherrypy.HTTPError(400, 
                                    ("Unrecognized format: %s.  Possible formats are: " % rtnfmt) + ', '.join(kwargs['_formats']))
                	
    return wrapped_f





# knownXSLT = { }
#
# class FileResolver(etree.Resolver):
#     def __init__(self):
#         parser = etree.XMLParser()
#         parser.resolvers.add(self)
#
#     def resolve(self, url, pubid, context):
#         return os.path.join(os.path.dirname(__file__), 'cts2xform/xsl/%s' % url)
#
# foo = FileResolver()
#
# def toHTML(rval, ns=None, **kwargs):
#     if hasattr(rval, 'resource'):
#         if rval.resource in knownXSLT:
#             # kwargs['xslt'] = knownXSLT[rval.resource]
#
#             xsltdocname = os.path.join(os.path.dirname(__file__), 'cts2xform/xsl/%s.xsl' % knownXSLT[rval.resource])
#             style = etree.XSLT(etree.parse(xsltdocname))
#             doc   = etree.XML(rval.toxml())
#             return etree.tostring(style(doc)), 'text/html;charset=UTF-8'
#
#     return toXML(rval, ns, **kwargs)
            
    

class BaseNode(object):
    """ BaseNode represents a REST node that expects a value on it, such
        as "concept/<val>".  If no value is supplied, this is a great place
        to display a menu and send the user on their way.
        
        BaseNode requires three additional parameters:
        
        label      - the label for the form (e.g. "Concept SCTID")
        extension  - (opt) additional information for the menu (see menu below)   
        value      - default value     
    """
    menu = htmlHead + '''
<html>
<body>
<script>
function validateForm()
{
    var x=document.forms["in"]["value"].value;
    var url = '%(path)s';
    if (x==null || x=="")
      {
      alert("Value must be supplied");
      return false;
      }
    if (url.match(/~/))
    {
       url = url.replace(/~/,x);
    }
    else
    {
        if (!/\/$/.test(url))
            url = url + '/';
        url = url + x;
    }
    document.forms["in"].action = url;
    document.forms["in"]["value"].removeAttribute('name');
}
</script>
<h2>%(title)s</h2>
<form name="in" method="GET" onsubmit="return validateForm()">
    <b>%(label)s:</b>
    <input type="text" name="value" value="%(value)s" size="40"/> <br/>
    %(extension)s
    <br/>
    <input type="submit" />
</form>
</body>
</html>'''

    title     = ""
    extension = ""
    value     = ""
    relpath   = None
    formats   = {}
    _cp_config = {
        'tools.auth_basic.no_auth': False}


    @cherrypy.expose
    @cherrypy.tools.allow()
    def index(self, *args, **kwargs):
        """ Invoked with no additional path elements
        @param args: empty - there are no path elements
        @param kwargs: parameters
        @return: Menu for particular node
        """
        # TODO: There has to be a better way of doing this...
        _vars = {k:getattr(self,k) for k in dir(self) if not k.startswith('_')}
        _vars['path'] = cherrypy.request.script_name+ (self.relpath if self.relpath else cherrypy.request.path_info)
        return self.menu % _vars

    @cherrypy.expose
    @cherrypy.tools.allow()
    def submitValue(self, value=None, *args, **kwargs):
        """ Invoked when the menu is submitted
        @param value: Supplied value
        @param args: Additional path arguments (none)
        @param kwargs: Parameters
        @return:
        """
        if value:
            raise cherrypy.HTTPRedirect(URLUtil.appendParams(value + ('/' + '/'.join(args) if args else ''),kwargs))

    
    def redirect(self, newURL, parmsToRemove=None, parmsToAdd=None, path=None):
        if not parmsToRemove: parmsToRemove=[]
        if not parmsToAdd: parmsToAdd={}
        if not path: path=None
        
        for p in parmsToRemove:
            self._kwargs.pop(p, None)       
        kwargs = dict([(k,v) for (k,v) in self._kwargs.items() if not k.startswith('_')])    
        raise cherrypy.HTTPRedirect(URLUtil.appendParams(newURL + ('/' + '/'.join(path) if path else ''),
                                                          dict(parmsToAdd, **kwargs)))
    
    def unknownPath(self, base, *args):
        return None, (404, "Unrecognized path: %s" % (base + '/' + '/'.join(args)))
