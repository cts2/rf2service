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
from server.RF2BaseNode import RF2BaseNode
from rf2db.utils.sctid import sctid

from rf2db.db.RF2FileCommon import global_rf2_parms
from rf2db.db.RF2DescriptionFile import DescriptionDB, description_parms, description_list_parms
from rf2db.db.RF2DescriptionTextFile import DescriptionTextDB, description_match_parms
from rf2db.db.RF2ConceptFile import ConceptDB, concept_parms


from server.config.Rf2Entries import settings



descdb =  DescriptionDB()
concdb =  ConceptDB()
desctextdb = DescriptionTextDB()


class Description(RF2BaseNode):
    title     = "Read description by description ID"
    label     = "Description SCTID"
    value = settings.refDesc
        
    @expose
    def default(self, desc=None, **kwargs):
        if not desc or desc=='concept':
            return self.index(**kwargs)
        if not sctid.isValid(desc):
            return None, (400, "Invalid description sctid: %s" % desc)
        if not description_parms.validate(**kwargs):
            return None, (404, description_parms.invalidMessage(**kwargs))
        dbrec = descdb.getDescriptionById(desc, description_parms.parse(**kwargs))
        return dbrec, (404, "Description id %s not found" % desc)           

class Descriptions(RF2BaseNode):
    title = "Find descriptions matching supplied text"
    label = "Match Text"
    value = settings.refMatchvalue

    
    @expose
    def default(self, *_, **kwargs):
        if not description_match_parms.validate(**kwargs):
            return None, (404, description_match_parms.invalidMessage(**kwargs))
        parmlist = description_match_parms.parse(**kwargs)
        return descdb.asDescriptionList(desctextdb.getDescriptions(parmlist), parmlist)
        

class DescriptionsForConcept(RF2BaseNode):
    label = "Concept SCTID"
    value = settings.refConcept
    relpath = "/concept/~/descriptions"

    @expose
    def default(self, concept, **kwargs):
        if not description_list_parms.validate(**kwargs):
            return None, (404, description_list_parms.invalidMessage(**kwargs))
        parmlist = description_list_parms.parse(**kwargs)
        return descdb.asDescriptionList(descdb.getConceptDescription(concept, parmlist), parmlist),\
               (404, "Description for concept %s not found" % concept)


class ConceptForDescription(RF2BaseNode):
    title = "Read concept record for description sctid"
    label = "Description SCTID"
    value = settings.refDesc
    relpath = "/description/~/concept"
            
    @expose
    def default(self, desc=None, **kwargs):
        if not sctid.isValid(desc):
            return None, (400, "Invalid description sctid: %s" % desc)
        if not description_parms.validate(**kwargs):
            return None, (404, description_parms.invalidMessage(**kwargs))
        conc = descdb.getConceptIdForDescription(desc, description_parms.parse(**kwargs))
        
        if conc:
            concrec = concdb.getConcept(conc, concept_parms.parse(**kwargs))
            return concrec, (404, "Concept for concept %s not found" % conc)
        else:
            return conc, (404, "Description for SCTID %s not found" % desc)




