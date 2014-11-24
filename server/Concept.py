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
from server.RF2BaseNode import RF2BaseNode, global_iter_parms
from rf2db.utils.sctid import sctid


from rf2db.db.RF2ConceptFile import ConceptDB, concept_parms, concept_list_parms, new_concept_parms, \
    update_concept_parms, delete_concept_parms
from server.Description import DescriptionsForConcept
from server.config.Rf2Entries import settings


concdb = ConceptDB()
# next step - pick up the represented namespace

class Concept(RF2BaseNode):
    title = "Read RF2 concept by concept id"
    label = "Concept SCTID"
    value = settings.refConcept

    @expose
    def default(self, concept=None, **kwargs):
        if concept == 'descriptions':
            return DescriptionsForConcept().index(**kwargs)
        if not concept_parms.validate(**kwargs):
            return None, (404, concept_parms.invalidMessage(**kwargs))

        dbrec = concdb.getConcept(long(sctid(concept)), concept_parms.parse(**kwargs))
        return dbrec, (404, "Concept %s not found" % concept)

    @expose("POST")
    def new(self, changeseturi=None, **kwargs):
        if not new_concept_parms.validate(**kwargs):
            return None, (404, new_concept_parms.invalidMessage(**kwargs))

        # A POST cannot supply an SCTID
        kwargs.pop('sctid', None)
        dbrec = concdb.newConcept(new_concept_parms.parse(**kwargs))
        if dbrec:
            self.redirect('/concept/%s' % dbrec.id)
        # TODO: figure out the correct error to return here
        return None, (404, "Unable to create concept")

    @expose(methods="PUT")
    def update(self, concept=None, **kwargs):
        if not update_concept_parms.validate(**kwargs):
            return None, (404, update_concept_parms.invalidMessage(**kwargs))

        # Update an existing concept
        return concdb.updateConcept(concept, update_concept_parms.parse(**kwargs))

    @expose(methods=["DELETE"])
    def delete(self, concept=None, **kwargs):
        if not delete_concept_parms.validate(**kwargs):
            return None, (404, delete_concept_parms.invalidMessage(**kwargs))
        return concdb.deleteConcept(concept, delete_concept_parms.parse(**kwargs))


class Concepts(RF2BaseNode):
    title = "List concepts starting after"
    label = "Concept SCTID"
    value = 0
    extensions = RF2BaseNode.extensions + [global_iter_parms]

    @expose
    def default(self, **kwargs):
        if not concept_list_parms.validate(**kwargs):
            return None, (404, concept_list_parms.invalidMessage(**kwargs))
        parmlist = concept_list_parms.parse(**kwargs)
        return concdb.asConceptList(concdb.getAllConcepts(parmlist),parmlist)

