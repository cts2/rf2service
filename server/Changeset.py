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
from rf2db.db.RF2ChangeSetFile import add_changeset_parms, changeset_parms, validate_changeset_parms

from rf2db.db.RF2ChangeSetFile import ChangeSetDB

csdb = ChangeSetDB()
# next step - pick up the represented namespace

class Changeset(RF2BaseNode):
    title = "Read RF2 changeset by changeset id"
    label = "Changeset UUID"

    @expose
    @validate(changeset_parms)
    def default(self, parms, **_):
        dbrec = csdb.get_changeset(**parms.dict)
        return dbrec, (404, "Change set %s not found" % parms.changeset)


    @expose
    def index(self, parms):
        return None, (501, "Changeset list not implemented")

    @expose("POST")
    @validate(add_changeset_parms)
    def new(self, parms, **_):
        dbrec = csdb.new_changeset(**parms.dict)
        if dbrec:
            parms.changeset = dbrec.changeset
            self.redirect('changeset/%s' % dbrec.changeset)
        return None, (500, "Create new changeset failed")

    @expose(methods="PUT")
    def update(self, parms, **kwargs):
        # Update an existing concept
        return None, (501, "Update changeset not implemented")

    @expose(methods=["DELETE"])
    @validate(changeset_parms)
    def delete(self, parms, **_):
        # TODO - format the return parameters
        csdb.rollback(**parms.dict)
        return """<!DOCTYPE html><html><body>%s deleted</body></html>""" % parms.changeset, (0,'')

    @expose(methods=["PUT"])
    @validate(changeset_parms)
    def commit(self, parms, **_):
        # TODO - return the concept id's, etc that are committed
        csdb.commit(**parms.dict)
        return """<!DOCTYPE html><html><body>%s committed</body></html>""" % parms.changeset, (0,'')



