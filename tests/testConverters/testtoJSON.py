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

import unittest
import json

from server.utils.SetConfig import setConfig
setConfig()
from server.converters.tojson import as_json

from rf2db.utils.jsonutils import cleanJson
from rf2db.parsers.RF2BaseParser import RF2Description


class JSONConverterTestCase(unittest.TestCase):
    def test_tojson(self):
        desc = RF2Description(
            '517048016\t20100131\t1\t900000000000380005\t10027005\ten\t900000000000003001\tPatchy (qualifier value)\t900000000000020002')
        jsonstr, mimetype = as_json(desc)
        self.assertEqual('application/json;charset=UTF-8', mimetype)
        self.assertDictEqual(cleanJson(
            {
                "_xmlns": "http://snomed.info/schema/rf2",
                "Description": {
                    "id": "517048016",
                    "effectiveTime": "20100131",
                    "active": "1",
                    "moduleId": "900000000000380005",
                    "conceptId": "10027005",
                    "languageCode": "en",
                    "typeId": "900000000000003001",
                    "term": "Patchy (qualifier value)",
                    "caseSignificanceId": "900000000000020002"
                }
            }), cleanJson(json.loads(jsonstr)))


if __name__ == '__main__':
    unittest.main()
