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
from server.BaseNode import expose
from server.RF2BaseNode import RF2BaseNode, validate


from rf2db.db.RF2LanguageFile import LanguageDB, language_parms, language_concept_parms, language_desc_parms

from server.config.Rf2Entries import settings

langdb = LanguageDB()


class Language(RF2BaseNode):
    title = "Read language entry by id"
    label = "Language Refset UUID"
    value = ''

    @expose
    @validate(language_parms)
    def default(self, parms, **_):
        return langdb.read(**parms.dict), (404, "Refset entry for %s not found" % parms.uuid)

class LanguagesForConcept(RF2BaseNode):
    title = "Read RF2 language refset for a given concept id"
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/languages"

    @expose
    @validate(language_concept_parms)
    def default(self, parms, **_):
        return langdb.as_list(langdb.get_entries_for_concept(**parms.dict), parms)


class LanguagesForDescription(RF2BaseNode):
    title = "Read RF2 language refset for a given description id"
    label = "Description SCTID"
    value = settings.refDesc
    relpath = "/description/~/languages"

    @expose
    @validate(language_desc_parms)
    def default(self, parms, **_):
        return langdb.as_list(langdb.get_entries_for_description(**parms.dict), parms)


