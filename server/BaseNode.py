# -*- coding: utf-8 -*-
# Copyright (c) 2014, Mayo Clinic
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
import types


from rf2db.utils import listutils, urlutil
from server.utils import negotiateFormat
from server.converters.toxml import as_xml
from server.converters.tojson import as_json
from server.converters.tohtml import as_html

htmlHead = "<!DOCTYPE html>"
xmlHead = '<?xml version="1.0" encoding="UTF-8"?>'
xmlVal = xmlHead + '\n<val>%s</val>'

def expose(func=None, methods=None):

    def expose_(func):

        @cherrypy.tools.allow(methods=methods)
        @cherrypy.expose
        def wrapped_f(self, *args, **kwargs):

            # Make a local image of the arguments for inside reference
            self._kwargs = kwargs.copy()
            if kwargs.get('_inside', False):
                # The innermost formatters trump the outer
                kwargs['_formats'] = dict(list(kwargs['_formats'].items()) + list(self.formats.items()))
                # As does the namespace
                if self.namespace:
                    kwargs['_ns'][0] = self.namespace
                return func(self, *args, **kwargs)

            # Acquire the required return format information and strip the bypass information
            rtnfmt = kwargs.pop('format', None)

            kwargs.pop('bypass', None)

            kwargs['_formats'] = {'xml':  as_xml,
                                  'json': as_json,
                                  'html': as_html}.copy()
            kwargs['_ns'] = [None]
            if self.namespace:
                kwargs['_ns'][0] = self.namespace
            for (k, v) in list(self.formats.items()):
                kwargs['_formats'][k] = v
            kwargs['_inside']  = True


            # Function can return one of:
            # formatted string           - to be returned directly to the caller, unformatted
            # class                      - assumed to have a toxml() function
            # tuple                      - (rval, (error code, error message))
            #                               rval is string or class as above

            rtn = func(self, *args, **kwargs)

            rval, (err, msg) = rtn if isinstance(rtn, (list, tuple)) else (rtn, (500, 'Internal Server Error'))
            if not rval:
                raise cherrypy.HTTPError(err, msg)
            if str(rval).startswith(htmlHead):
                return rval
            if not rtnfmt:
                rtnfmt = negotiateFormat.negotiate_format(list(kwargs['_formats'].keys()), cherrypy.request.headers)
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


    if isinstance(func, (types.FunctionType, types.MethodType)):
        return expose_(func)
    elif func is not None:
        methods = func
    return expose_


class BaseNode(object):
    """ BaseNode represents a REST node that expects a value on it, such
        as "concept/<val>".  If no value is supplied, this is a great place
        to display a menu and send the user on their way.
        
        BaseNode requires three additional parameters:
        
        label      - the label for the form (e.g. "Concept SCTID")
        extension  - (opt) additional information for the menu (see menu below)   
        value      - default value     
    """
    def buildpath(self):
        """ Return the javascript segment needed to generate a URL out of the parameters.  If C{self.relpath} is present
            and it contains the '~' metacharacter, then we just use it.  Otherwise, we add the value onto the end of
            the current path.
        """
        basepath = urlutil.href_settings.root + (self.relpath if self.relpath else cherrypy.request.path_info)
        if basepath.find('~') < 0:
            basepath += ('' if basepath.endswith('/') else '/') + '~'
        if cherrypy.request.query_string:
            basepath += ('&' if basepath.find('?') >= 0 else '?') + cherrypy.request.query_string
        return basepath


    menu = htmlHead + '''<html>
<body>
<script>
function validateForm()
{
    var x=document.forms["in"]["value"].value;
    var url = '%(path)s';
    if (x==null || x=="") {
      alert("Value must be supplied");
      return false;
    }
    document.forms["in"].action = url.replace(/~/,x);
    x = document.forms["in"].action;
    document.forms["in"]["value"].removeAttribute('name');
    var inputs = document.getElementsByTagName('input')
    
    for (var i = 0, len = inputs.length - 1; i < len; i++) {
        if (!inputs[i].value)
        {
            inputs[i].removeAttribute('name');
        }
    }

}
</script>
<h2>%(title)s</h2>
<form name="in" method="GET" onsubmit="return validateForm()">
    <b>%(label)s:</b>
    <input type="text" name="value" value="%(value)s" size="40"/><br/>
    %(extension)s
    <br/>
    <input type="submit" />
</form>
</body>
</html>'''

    title = ""
    extensions = []
    value = ""
    relpath= None
    formats   = {}
    _cp_config = {
        'tools.auth_basic.no_auth': False}


    @cherrypy.expose
    @cherrypy.tools.allow()
    def index(self, *_, **__):
        """ Invoked with no additional path elements
        @param args: empty - there are no path elements
        @param kwargs: parameters
        @return: Menu for particular node
        """
        # TODO: There has to be a better way of doing this...
        self.extension = [''.join(self.extensions)]
        _vars = {k: getattr(self,k) for k in dir(self) if not k.startswith('_')}
        _vars['path'] = self.buildpath()
        _vars['extension'] = '\n\t'.join(self.extensions)
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
            urlutil.redirect(urlutil.append_params(value + ('/' + '/'.join(args) if args else ''),kwargs))

    
    def redirect(self, newURL, parmsToRemove=None, parmsToAdd=None, path=None):
        if not parmsToRemove: parmsToRemove=[]
        if not parmsToAdd: parmsToAdd={}
        if not path: path=None
        
        for p in parmsToRemove:
            self._kwargs.pop(p, None)       
        kwargs = dict([(k, v) for (k, v) in list(self._kwargs.items()) if not k.startswith('_')])
        urlutil.redirect(urlutil.append_params(newURL + ('/' + '/'.join(path) if path else ''),
                                                          dict(parmsToAdd, **kwargs)))
    
    def unknownPath(self, base, *args):
        return None, (404, "Unrecognized path: %s" % (base + '/' + '/'.join(args)))
