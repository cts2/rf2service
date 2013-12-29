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
from server.converters.toxml import as_xml, prettyxml
from rf2db.utils.xmlutils import diffxml
from rf2db.parsers.RF2BaseParser import RF2Description


class XMLConverterTestCase(unittest.TestCase):
    def test_toxml(self):
        desc = RF2Description('517048016\t20100131\t1\t900000000000380005\t10027005\ten\t900000000000003001\tPatchy (qualifier value)\t900000000000022005')
        xml,mimetype = as_xml(desc)
        self.assertEqual(mimetype,'application/xml;charset=UTF-8')
        self.assertTrue(diffxml("""<?xml version="1.0" encoding="UTF-8"?>
<Description xmlns="http://snomed.info/schema/rf2">
    <id>517048016</id>
    <effectiveTime>20100131</effectiveTime>
    <active>1</active>
    <moduleId>900000000000380005</moduleId>
    <conceptId>10027005</conceptId>
    <languageCode>en</languageCode>
    <typeId>900000000000003001</typeId>
    <term>Patchy (qualifier value)</term>
    <caseSignificanceId>900000000000022005</caseSignificanceId>
</Description>""", xml))
        xml,mimetype = as_xml(xml)
        self.assertEqual(mimetype,'application/xml;charset=UTF-8')
        self.assertTrue(diffxml("""<?xml version="1.0" encoding="UTF-8"?>
<Description xmlns="http://snomed.info/schema/rf2">
    <id>517048016</id>
    <effectiveTime>20100131</effectiveTime>
    <active>1</active>
    <moduleId>900000000000380005</moduleId>
    <conceptId>10027005</conceptId>
    <languageCode>en</languageCode>
    <typeId>900000000000003001</typeId>
    <term>Patchy (qualifier value)</term>
    <caseSignificanceId>900000000000022005</caseSignificanceId>
</Description>""", xml))


if __name__ == '__main__':
    unittest.main()
