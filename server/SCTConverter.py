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
# Redistributions in binary form must reproduce the above copyright notice,
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
import re

from server.BaseNode import expose, BaseNode
from server.utils.SCTConverterGateway import SCTConverterGateway
from rf2db.parameterparser.ParmParser import booleanparam

from server.config.Rf2Entries import settings


class SCTConverter(BaseNode):
    namespace = None
    label = "Subject SCTID"
    value = "who:" + settings.refConcept
    title = "Evaluate a compositional grammar expression"
    extensions = BaseNode.extensions + [
        """<p><b>Expression</b><p><textarea name="expr" rows=5 cols=80> 18526009| Disorder of appendix (disorder) |+
	302168000| Inflammation of large intestine (disorder) |+
	64572001| Disease (disorder) |:
	{ 116676008| Associated morphology (attribute) |=23583003| Inflammation (morphologic abnormality) |,
	363698007| Finding site (attribute) |=66754008| Appendix structure (body structure) | }</textarea></p> """]
    parser = None

    @expose(("POST", "GET"))
    def default(self, subject, expr='', primitive=True, shorturis=False, removesct=False, **_):
        if not self.parser:
            self.parser = SCTConverterGateway()
        return (self.parser.parse(subject, booleanparam.v(primitive, True), re.sub(r'\s+', '', expr, flags=re.DOTALL)),
        (404, "Unable to parse expression"))


@expose(("POST", "GET"))
def classify(self, expr='', **_):
    return (None, (500, "Not Implemented"))