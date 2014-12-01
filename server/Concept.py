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
from server.RF2BaseNode import RF2BaseNode, global_iter_parms, validate
from rf2db.utils.sctid import sctid

from rf2db.db.RF2ConceptFile import ConceptDB, concept_parms, concept_list_parms, new_concept_parms, \
    update_concept_parms, delete_concept_parms
from server.config.Rf2Entries import settings

concdb = ConceptDB()


class Concept(RF2BaseNode):
    title = "Read RF2 concept by concept id"
    label = "Concept SCTID"
    value = settings.refConcept

    @expose
    @validate(concept_parms)
    def default(self, parms, **kwargs):
        dbrec = concdb.read(int(sctid(parms.concept)), **parms.dict)
        return dbrec, (404, "Concept %s not found" % parms.concept)

    @expose("POST")
    @validate(new_concept_parms)
    def new(self, parms, **kwargs):
        # A POST cannot supply an SCTID
        kwargs.pop('sctid', None)
        dbrec = concdb.add(**parms.dict)
        if dbrec:
            self.redirect('/concept/%s' % dbrec.id)
        # TODO: figure out the correct error to return here
        return None, (404, "Unable to create concept")

    @expose(methods="PUT")
    @validate(update_concept_parms)
    def update(self, parms, concept, **_):
        return concdb.update(concept, **parms.dict)

    @expose(methods=["DELETE"])
    @validate(delete_concept_parms)
    def delete(self, parms, concept, **_):
        return concdb.delete(concept, **parms.dict)


class Concepts(RF2BaseNode):
    title = "List concepts starting after"
    label = "Concept SCTID"
    value = 0
    extensions = RF2BaseNode.extensions + [global_iter_parms]

    @expose
    @validate(concept_list_parms)
    def default(self, parms, **_):
        return concdb.as_list(concdb.getAllConcepts(**parms.dict), parms)

