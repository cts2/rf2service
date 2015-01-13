# -*- coding: utf-8 -*-
# Copyright (c) 2013, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
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
from server.BaseNode import expose, xmlVal
from server.RF2BaseNode import RF2BaseNode, global_iter_parms, validate
from rf2db.utils.sctid import sctid

from rf2db.db.RF2DescriptionFile import DescriptionDB, description_parms, \
    pref_description_parms, description_for_concept_parms, new_description_parms, update_description_parms, \
    delete_description_parms, fsn_parms, base_parms
from rf2db.db.RF2DescriptionTextFile import DescriptionTextDB, description_match_parms
from rf2db.db.RF2ConceptFile import ConceptDB, concept_parms
from rf2db.db.RF2LanguageFile import LanguageDB

from server.config.Rf2Entries import settings

descdb = DescriptionDB()
concdb = ConceptDB()
desctextdb = DescriptionTextDB()
langdb = LanguageDB()


class Description(RF2BaseNode):
    title = "Read description by description ID"
    label = "Description SCTID"
    value = settings.refDesc

    @expose
    @validate(description_parms)
    def default(self, parms, **kwargs):
        dbrec = descdb.read(int(sctid(parms.desc)), **parms.dict)
        return dbrec, (404, "Description id %s not found" % parms.desc)

    @expose("POST")
    @validate(new_description_parms)
    def new(self, parms, **kwargs):
        # A POST cannot supply a description sctid
        kwargs.pop('desc', None)
        dbrec = descdb.add(**parms.dict)
        if isinstance(dbrec, basestring):
            return None, (400, dbrec)
        elif not dbrec:
            return None, (404, "Unable to create description record")
        self.redirect('/description/%s' % dbrec.id)


    @expose(methods="PUT")
    @validate(update_description_parms)
    def update(self, parms, desc, **_):
        return concdb.update(desc, **parms.dict)

    @expose(methods=["DELETE"])
    @validate(delete_description_parms)
    def delete(self, parms, desc, **_):
        return concdb.delete(desc, **parms.dict)


class Descriptions(RF2BaseNode):
    title = "Find descriptions matching supplied text"
    label = "Match Text"
    value = settings.refMatchvalue
    extensions = RF2BaseNode.extensions + [
        """<p><b>Match Algorithm:</b>
<input type="radio" name="matchalgorithm" value="wordstart" checked="True">Word Starts With</input>
<input type="radio" name="matchalgorithm" value="contains">Term Contains</input>
<input type="radio" name="matchalgorithm" value="startswith">Term Starts With</input>
<input type="radio" name="matchalgorithm" value="endswith">Term Ends With</input>
<input type="radio" name="matchalgorithm" value="exactmatch">Exact Term Match</input>
<input type="radio" name="matchalgorithm" value="wordend">Word Ends With</input>
</p>""",
        global_iter_parms]


    @expose
    @validate(description_match_parms)
    def default(self, parms, **_):
        return descdb.as_list(desctextdb.getDescriptions(**parms.dict), parms)


class DescriptionsForConcept(RF2BaseNode):
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/descriptions"
    extensions = RF2BaseNode.extensions + [global_iter_parms]

    @expose
    @validate(description_for_concept_parms)
    def default(self, parms, **_):
        return descdb.as_list(descdb.getConceptDescription(parms.concept, **parms.dict), parms), \
               (404, "Description for concept %s not found" % parms.concept)


class FSNForConcept(RF2BaseNode):
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/fsn"

    @expose
    @validate(fsn_parms)
    def default(self, parms, **_):
        return descdb.fsn(**parms.dict), (404, "FSN for concept %s not found" % parms.concept)

class ConceptBase(RF2BaseNode):
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/base"

    @expose
    @validate(base_parms)
    def default(self, parms, **_):
        base = descdb.base(**parms.dict)
        if base:
            base = xmlVal % base
        return base, (404, "FSN for concept %s not found" % parms.concept)


class PreferredDescriptionForConcept(RF2BaseNode):
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/prefdescription"

    @expose
    @validate(pref_description_parms)
    def default(self, parms, **_):
        pt_entry = langdb.preferred_term_for_concepts(parms.concept, **parms.dict)
        if not pt_entry:
            return None, (404, "Preferred term for concept %s not found" % parms.concept)
        desc = pt_entry[str(parms.concept)][1]
        return descdb.read(desc, **parms.dict), \
               (404, "Description id %s not found" % desc)


class ConceptForDescription(RF2BaseNode):
    title = "Read concept record for description sctid"
    label = "Description SCTID"
    value = settings.refDesc
    relpath = "/description/~/concept"

    @expose
    def default(self, desc=None, **args):
        if not sctid.isValid(desc):
            return None, (400, "Invalid description sctid: %s" % desc)
        conc = descdb.getConceptIdForDescription(desc, **args)

        if conc:
            concrec = concdb.read(conc, **args)
            return concrec, (404, "Concept for concept %s not found" % conc)
        return None, (404, "Description for SCTID %s not found" % desc)




