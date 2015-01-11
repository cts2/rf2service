# -*- coding: utf-8 -*-
# Copyright (c) 2014, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
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
from rf2db.db.RF2ChangeSetFile import ChangeSetDB
from rf2db.db.RF2ComplexMapFile import ComplexMapDB
from rf2db.db.RF2LanguageFile import LanguageDB
from rf2db.db.RF2ModuleDependencyFile import ModuleDependencyDB
from rf2db.db.RF2SimpleMapFile import SimpleMapDB
from rf2db.db.RF2SimpleReferencesetFile import SimpleReferencesetDB
from rf2db.db.RF2RefsetWrapper import global_refset_parms

refsets = [(ChangeSetDB, 'changeset/'),
           (ComplexMapDB, 'complexmap/'),
           (LanguageDB, 'language/'),
           (ModuleDependencyDB, 'moduledependency/'),
           (SimpleReferencesetDB, 'simplerefset/'),
           (SimpleMapDB, 'simplemap/')]

class GenericRefset(RF2BaseNode):
    title = "Read RF2 refset by id"
    label = "Refset UUID"
    value = ''

    @expose
    @validate(global_refset_parms)
    def default(self, parms, **kwargs):
        for db, base in refsets:
            rval = db().read(**dict(parms.dict, **kwargs))
            if rval:
                self.redirect(base, parmsToRemove=['uuid'], path=[rval.referencedComponentId.uuid]) \
                    if db == ChangeSetDB else self.redirect(base)
        return None, (404, "Refset entry %s not found" % parms.uuid)
