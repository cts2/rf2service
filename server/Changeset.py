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

from server.BaseNode import expose, xmlVal
from server.RF2BaseNode import RF2BaseNode, validate
from rf2db.db.RF2ChangeSetFile import add_changeset_parms, changeset_parms, update_changeset_parms, \
    list_changeset_parms, ChangeSetDB
from server.config.Rf2Entries import settings

csdb = ChangeSetDB()


class Changeset(RF2BaseNode):
    title = "Read RF2 changeset by changeset id"
    label = "Changeset Name or UUID"
    value = settings.refChangeSet

    @expose
    @validate(changeset_parms)
    def default(self, parms, **_):
        dbrec = csdb.read(**parms.dict)
        return dbrec, (404, "Change set %s not found" % parms.changeset)

    @expose
    @validate(changeset_parms)
    def details(self, parms, **_):
        dbrec = csdb.read_details(**parms.dict)
        return dbrec, (404, "Change set %s not found" % parms.changeset)


    @expose("POST")
    @validate(add_changeset_parms)
    def new(self, parms, **_):
        dbrec = csdb.new(**parms.dict)
        if dbrec:
            parms.changeset = dbrec.changeset
            self.redirect('changeset/%s' % dbrec.changeset)
        return None, (404, csdb.invalid_new_reason(**parms.dict))

    @expose(methods="PUT")
    @validate(update_changeset_parms)
    def update(self, parms, **_):
        return csdb.update(**parms.dict), (404, csdb.invalid_update_reason(**parms.dict))


    @expose(methods=["DELETE"])
    @validate(changeset_parms)
    def delete(self, parms, **_):
        # TODO - format the return parameters
        csdb.rollback(**parms.dict)
        return xmlVal % (parms.changeset + " rolled back"), (0, '')

    @expose(methods=["PUT"])
    @validate(changeset_parms)
    def commit(self, parms, **_):
        # TODO - return the concept id's, etc that are committed
        csdb.commit(**parms.dict)
        return xmlVal % (parms.changeset + " committed"), (0, '')

    @expose
    @validate(list_changeset_parms)
    def list(self, parms, **_):
        return csdb.as_list(csdb.list(**parms.dict), parms)
