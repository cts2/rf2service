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

from server.BaseNode    import expose
from server.RF2BaseNode import RF2BaseNode


from rf2db.db.RF2LanguageFile import LanguageDB, language_list_parms

from server.config.Rf2Entries import settings

langdb = LanguageDB()


class LanguagesForConcept(RF2BaseNode):
    title = "Read RF2 language refset for a given concept id"
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/languages"

    @expose
    def default(self, concept, **kwargs):
        if not language_list_parms.validate(**kwargs):
            return None, (404, language_list_parms.invalidMessage(**kwargs))
        parmlist = language_list_parms.parse(**kwargs)
        return langdb.as_reference_set(langdb.get_entries_for_concept(concept, parmlist), parmlist)


class LanguagesForDescription(RF2BaseNode):
    title = "Read RF2 language refset for a given description id"
    label = "Description SCTID"
    value = settings.refDesc
    relpath = "/description/~/languages"

    @expose
    def default(self, desc, **kwargs):
        if not language_list_parms.validate(**kwargs):
            return None, (404, language_list_parms.invalidMessage(**kwargs))
        parmlist = language_list_parms.parse(**kwargs)
        return langdb.as_reference_set(langdb.get_entries_for_description(desc, parmlist), parmlist)


