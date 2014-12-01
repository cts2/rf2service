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

from server.BaseNode import expose
from server.RF2BaseNode import RF2BaseNode, global_iter_parms, validate

from rf2db.db.RF2ComplexMapFile import ComplexMapDB, complexmap_list_parms
from server.config.Rf2Entries import settings

_maps_tmpl = """
        <p>
            <br/><b>Restrict to map id(s):</b>
            %s
        </p>"""
_maplist_tmpl = """<input type="checkbox" name="refset" value=%s>%s</input>"""

complexmap_db = ComplexMapDB()

class ComplexMapBase(object):
    def common(self, parms):
        dbrec = complexmap_db.as_list(complexmap_db.get_complex_map(**parms.dict), parms)
        if dbrec: return dbrec
        rtn_message = "Complex map for"
        rtn_message += " refset %s" % parms.refset if parms.refset else ''
        rtn_message += " component %s" % parms.component if parms.component else ''
        rtn_message += " target %s" % parms.target if parms.target else ''
        rtn_message += " not found"
        return None, (404, rtn_message)

class ComplexMapById(RF2BaseNode, ComplexMapBase):
    title = "Query RF2 ComplexMap Refset"
    label = "Map SCTID"
    value = settings.refComplexMap
    relpath = '/complexmap/~'
    extensions = RF2BaseNode.extensions + [global_iter_parms]

    @expose
    @validate(complexmap_list_parms)
    def default(self, parms, **_):
        return self.common(parms)


class ComplexMapForSource(RF2BaseNode, ComplexMapBase):
    title = "Query RF2 ComplexMap Refset"
    label = "Source concept "
    value = settings.refComplexMapSource
    relpath = '/complexmap/source/~'
    _rsnames = ComplexMapDB().refset_names()
    extensions = RF2BaseNode.extensions + [global_iter_parms,
                                           _maps_tmpl % '\t\t\n'.join(_maplist_tmpl % e for e in _rsnames.items())]


    @expose
    @validate(complexmap_list_parms)
    def default(self, parms, **_):
        return self.common(parms)


class ComplexMapForTarget(RF2BaseNode, ComplexMapBase):
    title = "Query RF2 ComplexMap Refset"
    label = "Target concept "
    value = settings.refComplexMapTarget
    relpath = '/complexmap/target/~'
    _rsnames = ComplexMapDB().refset_names()
    extensions = RF2BaseNode.extensions + [global_iter_parms,
                                           _maps_tmpl % '\t\t\n'.join(_maplist_tmpl % e for e in _rsnames.items())]


    @expose
    @validate(complexmap_list_parms)
    def default(self, parms, **_):
        return self.common(parms)
