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
import cherrypy

from rf2db.db.RF2RelationshipFile import RelationshipDB, rel_parms, rel_source_parms, \
    rel_predicate_parms, rel_target_parms, new_rel_parms, del_rel_parms
from rf2db.db.RF2StatedRelationshipFile import StatedRelationshipDB
from rf2db.db.RF2ConceptFile import ConceptDB, concept_parms
from server.BaseNode import expose
from server.RF2BaseNode import RF2BaseNode, global_iter_parms, validate
from server.config.Rf2Entries import settings

reldb = RelationshipDB()
statedreldb = StatedRelationshipDB()
concdb = ConceptDB()

reltypes = """<b>Relationship Type: </b>
    <label>Stated: </label><input type="checkbox" name="stated" value="true" checked="checked"/>
    <label>Inferred: </label><input type="checkbox" name="inferred" value="true" checked="checked"/>
    <label>Additional: </label><input type="checkbox" name="additional" value="true" checked="checked"/>
    <label>Canonical Only: </label><input type="checkbox" name="canonical" value="true"/>
    <br/>"""


class Relationship(RF2BaseNode):
    title = "<p>Read RF2 relationship entry by relationship id</p>"
    label = "Relationship SCTID"
    value = settings.refRel

    @expose
    @validate(rel_parms)
    def default(self, parms, **_):
        dbrec = reldb.read(**parms.dict)
        return dbrec, (404, "Relationship record %s not found" % parms.rel)

    @expose("POST")
    @validate(new_rel_parms)
    def new(self, parms, **kwargs):
        # A POST cannot supply a relationship id
        kwargs.pop('id', None)
        dbrec = reldb.add(**parms.dict)
        if isinstance(dbrec, str):
            return None, (400, dbrec)
        elif not dbrec:
            return None, (500, "Unable to create relationship record")
        self.redirect('/relationship/%s' % dbrec.id)


    @expose(methods=["DELETE"])
    @validate(del_rel_parms)
    def delete(self, parms, rid, **_):
        return concdb.delete(rid, **parms.dict)


class Relationships(RF2BaseNode):
    label = "Relationship SCTID"
    value = settings.refConcept
    extensions = RF2BaseNode.extensions + ["""
    <br/><label><input type="radio" name="direct" value="source" checked="checked"/>Source of</label>
    <label><input type="radio" name="direct" value="predicate"/>Predicate of</label>
    <label><input type="radio" name="direct" value="target" />Target of</label><br/>""",
                                           global_iter_parms]

    @cherrypy.expose
    @cherrypy.tools.allow()
    def default(self, value=None, direct=None, **kwargs):
        raise cherrypy.HTTPRedirect(direct + ('/%s' % value) if value else '')


def validateAndExecute(cid, fctn, parms):
    if not concdb.read(cid, **parms.dict):
        return None, (404, "Concept %s doesn't exist" % cid)
    return reldb.as_list(fctn(cid, **parms.dict), parms)


class RelationshipsForSource(RF2BaseNode):
    title = "<p>Relationship entries for source SCTID</p>"
    label = "Subject SCTID"
    value = settings.refConcept
    extensions = RF2BaseNode.extensions + [reltypes, global_iter_parms]

    @expose
    @validate(rel_source_parms)
    def default(self, parms, **_):
        return validateAndExecute(parms.source, reldb.getSourceRecs, parms)


class RelationshipsForPredicate(RF2BaseNode):
    title = "<p>Relationship entries for predicate SCTID</p>"
    label = "Predicate SCTID"
    value = settings.refPredicate
    extensions = RF2BaseNode.extensions + [reltypes, global_iter_parms]


    @expose
    @validate(rel_predicate_parms)
    def default(self, parms, **_):
        return validateAndExecute(parms.predicate, reldb.getPredicateRecs, parms)


class RelationshipsForTarget(RF2BaseNode):
    title = "<p>Relationshp entries for target SCTID</p>"
    label = "Target SCTID"
    value = settings.refTargetConcept
    extensions = RF2BaseNode.extensions + [reltypes, global_iter_parms]


    @expose
    @validate(rel_target_parms)
    def default(self, parms, **_):
        return validateAndExecute(parms.target, reldb.getTargetRecs, parms)


