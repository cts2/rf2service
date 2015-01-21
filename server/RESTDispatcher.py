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
from server.Concept import Concept, Concepts
from server.Description import Description, Descriptions, DescriptionsForConcept, ConceptForDescription, \
    PreferredDescriptionForConcept, FSNForConcept, ConceptBase
from server.Relationship import Relationship, Relationships, RelationshipsForSource, RelationshipsForTarget, \
    RelationshipsForPredicate
from server.Language import LanguagesForConcept, LanguagesForDescription, Language
from server.SimpleRefset import SimpleRefsetByComponent, SimpleRefSet
from server.SimpleMap import SimpleMapByMapId, SimpleMapForSource, SimpleMapForTarget
from server.ComplexMap import ComplexMapById, ComplexMapForSource, ComplexMapForTarget
from server.Changeset import Changeset
from server.OtherRefsets import ModuleDependency
from server.GenericRefset import GenericRefset
from server.Server import ServerConf
from server.Root import Root
from auth.ihtsdoauth import License

# Note:  This function requires the python routes package - install with PIP

dispatcher = cherrypy.dispatch.RoutesDispatcher()

class Resource():
    controllers = {}
    def __init__(self, path, controller, method='GET', action='default'):
        """ Construct a path.  Paths are evaluated sequentially, so the most specific must occur first. Also note that
        both this function *and* CherryPy map the path to a controller and then map the HTTP methods to functions,
        meaning that you can't send a GET to one class and a PUT to another
        :param path: relative path to match.  Requests format
        :param controller: Class to instantiate
        :param method: method to match
        :param action: action to invoke based on method
        """
        self.controllers.setdefault(controller, controller())
        dispatcher.connect(path, path, controller=self.controllers[controller], action=action,
                           conditions=dict(method=[method]))

print("Connecting resources")
resources = [Resource(r'/', Root, action='index'),
             Resource(r'/config', ServerConf),
             Resource(r'/status', ServerConf, action='status'),
             Resource(r'/license', License, action='index'),
             Resource(r'/submit', License, action='submit', method='POST'),

             Resource(r'/refset', GenericRefset, action='index'),
             Resource(r'/refset/:uuid', GenericRefset),

             Resource(r'/concepts', Concepts, action='index'),
             Resource(r'/concepts/:after', Concepts),
             Resource(r'/concepts/', Concepts),
             Resource(r'/concept/languages', LanguagesForConcept, action='index'),
             Resource(r'/concept/prefdescription', PreferredDescriptionForConcept, action='index'),
             Resource(r'/concept/descriptions', DescriptionsForConcept, action='index'),
             Resource(r'/concept/:concept/descriptions/:matchvalue', DescriptionsForConcept),
             Resource(r'/concept/:concept/descriptions/', DescriptionsForConcept, action='index'),
             Resource(r'/concept/:concept/descriptions', DescriptionsForConcept),
             Resource(r'/concept/:concept/languages', LanguagesForConcept),
             Resource(r'/concept/:concept/prefdescription', PreferredDescriptionForConcept),
             Resource(r'/concept/:concept/fsn', FSNForConcept),
             Resource(r'/concept/:concept/base', ConceptBase),
             Resource(r'/concept/:concept', Concept, action='update', method='PUT'),
             Resource(r'/concept/:concept', Concept, action='delete', method='DELETE'),
             Resource(r'/concept/:concept', Concept),
             Resource(r'/concept', Concept, action='new', method='POST'),
             Resource(r'/concept', Concept, action='index'),

             Resource(r'/descriptions/:matchvalue', Descriptions),
             Resource(r'/descriptions/', Descriptions),
             Resource(r'/descriptions', Descriptions, action='index'),

             Resource(r'/description/concept', ConceptForDescription, action='index'),
             Resource(r'/description/languages', LanguagesForDescription, action='index'),
             Resource(r'/description/:desc/concept/', ConceptForDescription),
             Resource(r'/description/:desc/concept', ConceptForDescription),
             Resource(r'/description/:desc/languages', LanguagesForDescription),
             Resource(r'/description/:desc', Description, action='update', method='PUT'),
             Resource(r'/description/:desc', Description, action='delete', method='DELETE'),
             Resource(r'/description/:desc', Description),
             Resource(r'/description', Description, action='new', method='POST'),
             Resource(r'/description', Description, action='index'),

             Resource(r'/relationship/:rel', Relationship),
             Resource(r'/relationship', Relationship, action='index'),
             Resource(r'/relationships/source/:source', RelationshipsForSource),
             Resource(r'/relationships/source', RelationshipsForSource, action='index'),
             Resource(r'/relationships/predicate/:predicate', RelationshipsForPredicate),
             Resource(r'/relationships/predicate', RelationshipsForPredicate, action='index'),
             Resource(r'/relationships/target/:target', RelationshipsForTarget),
             Resource(r'/relationships/target', RelationshipsForTarget, action='index'),
             Resource(r'/relationships/:value', Relationships),
             Resource(r'/relationship/:rid', Relationship, action='delete', method='DELETE'),
             Resource(r'/relationship/source/:source/target/:target', Relationship, action='new', method='POST'),
             Resource(r'/relationship/source/:source/predicate/:predicate/target/:target', Relationship,
                      action='new', method='POST'),
             Resource(r'/relationships/', Relationships),
             Resource(r'/relationships', Relationships, action='index'),

             Resource(r'/language/:uuid', Language),
             Resource(r'/language', Language, action='index'),

             Resource(r'/moduledependency/:uuid', ModuleDependency),
             Resource(r'/moduledependency', ModuleDependency, action='index'),

             # Note: there can't be a refset called "component" -- so be it
             Resource(r'/simplerefset/component/:component', SimpleRefsetByComponent),
             Resource(r'/simplerefset/component', SimpleRefsetByComponent, action='index'),
             Resource(r'/simplerefset/:refset/component/:component', SimpleRefSet, action='update', method='PUT'),
             Resource(r'/simplerefset/:refset/component/:component', SimpleRefSet, action='delete', method='DELETE'),
             Resource(r'/simplerefset/:refset/component/:component', SimpleRefSet),
             # This allows for multiple components (component=a b c...)
             Resource(r'/simplerefset/:refset', SimpleRefSet, action='update', method='PUT'),
             Resource(r'/simplerefset/:refset', SimpleRefSet, action='delete', method='DELETE'),
             Resource(r'/simplerefset/:refset', SimpleRefSet),
             Resource(r'/simplerefset/', SimpleRefSet, action='new', method='POST'),
             Resource(r'/simplerefset/', SimpleRefSet),
             Resource(r'/simplerefset', SimpleRefSet, action='new', method='POST'),
             Resource(r'/simplerefset', SimpleRefSet, action='index'),

             Resource(r'/simplemap/source/:component', SimpleMapForSource),
             Resource(r'/simplemap/:refset/source/:component', SimpleMapForSource),
             Resource(r'/simplemap/source', SimpleMapForSource, action='index'),
             Resource(r'/simplemap/target/:target', SimpleMapForTarget),
             Resource(r'/simplemap/:refset/target/:target', SimpleMapForTarget),
             Resource(r'/simplemap/target', SimpleMapForTarget, action='index'),
             Resource(r'/simplemap/:refset', SimpleMapByMapId),
             Resource(r'/simplemap', SimpleMapByMapId, action='index'),
             Resource(r'/simplemap/', SimpleMapByMapId),

             Resource(r'/complexmap/source/:component', ComplexMapForSource),
             Resource(r'/complexmap/:refset/source/:component', ComplexMapForSource),
             Resource(r'/complexmap/source', ComplexMapForSource, action='index'),
             Resource(r'/complexmap/target/:target', ComplexMapForTarget),
             Resource(r'/complexmap/:refset/target/:target', ComplexMapForTarget),
             Resource(r'/complexmap/target', ComplexMapForTarget, action='index'),
             Resource(r'/complexmap/:refset', ComplexMapById),
             Resource(r'/complexmap', ComplexMapById, action='index'),
             Resource(r'/complexmap/', ComplexMapById),

             Resource(r'/changeset/:changeset/commit', Changeset, action='commit', method='PUT'),
             Resource(r'/changeset/:changeset', Changeset, action='update', method='PUT'),
             Resource(r'/changeset/:changeset', Changeset, action='delete', method='DELETE'),
             Resource(r'/changeset/:changeset/details', Changeset, action='details'),
             Resource(r'/changeset/:changeset/uuid', Changeset, action='uuid'),
             Resource(r'/changeset/:changeset', Changeset),
             Resource(r'/changeset/:csname', Changeset, action='new', method='POST'),
             Resource(r'/changeset', Changeset, action='index'),
             Resource(r'/changeset/', Changeset),
             Resource(r'/changeset', Changeset, action='new', method='POST'),
             Resource(r'/changesets', Changeset, action='list'), ]




