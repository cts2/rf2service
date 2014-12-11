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
# -*- coding: utf-8 -*-
import unittest
import urllib2
import os
import re

from rf2db.utils.xmlutils import prettyxml, diffxml
from server.utils.SetConfig import setConfig
setConfig()

def testxml(resource, xmltotest=None, testfile=None, save=False, printdiff=True):
    """ Compare the XML in resource to the supplied string or file
    @param resource - a resource or xml text to test
    @param xmltotest - xml text to test against
    @param testfile - file name containing xml text
    @param save - if true, write the xml for resource into testfile
    @param printdiff - if true, print out any differences
    @return whether resource and testxml/textfile are the same or not
    """
    assert (xmltotest or testfile) and not(xmltotest and testfile)
    if save and testfile:
        open(testfile, 'w').write(prettyxml(resource))
        print "SAVED: " + testfile
        rval = True
    else:
        if not xmltotest:
            xmltotest = open(testfile).read()
        rval = diffxml(resource.toxml() if hasattr(resource, 'toxml') else resource, xmltotest, printdiff=printdiff)
    return rval


from server.config.Rf2Entries import settings

service_uri = 'http://localhost:8081/rf2/'

urls = [
    ('concept/%s?format=xml' % settings.refConcept),
    ('description/%s?format=xml' % settings.refDesc)]


errorurls = [
    ('changeset/abc', (404, "Namespace sctpn not found")),
]

testdir = '/rf2/'
prefix = 't_'

dirname, _ = os.path.split(os.path.abspath(__file__))

replaces = ['http://', ':', '?', '=', '&amp;', '+']

json_ignore = []


class WebServerTestCase(unittest.TestCase):

    @staticmethod
    def cleanJson(json):
        json.pop('accessDate', None)
        for (k,v) in json.items():
            if isinstance(v, dict):
                WebServerTestCase.cleanJson(v)
        return json

    def straightdiff(self,old,new):
        olds = re.sub(r'accessDate([^Z]*)Z','accessDate="Z"',str(old)).strip()
        news = re.sub(r'accessDate([^Z]*)Z','accessDate="Z"',str(new)).strip()
        if olds == news:
            return None
        n = 0
        while n < len(olds) and n < len(news) and olds[n] == news[n]: n += 1
        nlow = max(n-30,0)
        rval = 'Mismatch\n'
        rval += 'old: ' + olds[nlow:n+20] + '\n'
        rval += '     ' + ' ' * min(30,n) + '^\n'
        rval += 'new: ' + news[nlow:n+20] + '\n'
        return rval

    def doTest(self, u):
        url = u.replace('?','?bypass=1&') if '?' in u else (u + '?bypass=1')
        print "READING", (service_uri+url).replace('&amp;','&')
        req = urllib2.Request(service_uri+url)
        response = urllib2.urlopen(req)
        the_page = response.read()

        mungedu = reduce(lambda s,r: s.replace(r,'_'), replaces, u)

        udir, ufile = os.path.split(mungedu)
        d = dirname + testdir + udir
        fname = os.path.join(d, prefix + ufile)
        if not os.path.exists(d):
            os.makedirs(d)
        print "TESTING:", fname
        if not os.path.exists(fname):
            print "Writing new file image"
            f = open(fname,'w')
            f.write(the_page)
            f.close()

        match_txt = open(fname, 'r').read()
        self.maxDiff = None
        if 'format=' not in u or 'format=xml' in u:
            error = 'xmldiff error' if not testxml(the_page, match_txt) else None
        elif 'format=json' in u:
            match_txt = match_txt
            self.assertDictEqual(self.cleanJson(eval(the_page)), self.cleanJson(eval(match_txt)))
            return True
        else:
            error = self.straightdiff(the_page, match_txt)
        if error:
            print 'URL', (service_uri+url).replace('&amp;','&')
            print error
        if error:
            print the_page
        return not bool(error)

    def doErrorTest(self, u, (code, text)):
        url = u.replace('?', '?bypass=1&') if '?' in u else (u + '?bypass=1')
        print "READING", (service_uri+url).replace('&amp;', '&')
        req = urllib2.Request(service_uri+url)
        try:
            e = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if e.code == code:
                return True

        print 'URL', (service_uri+url).replace('&amp;','&')
        print '\texpected: %s - %s' % (code, text)
        print '\treceived: %s - %s' % (e.code, e.msg)
        return False



    def testBasic(self):
        # To run this test:
        #    1) Set RF2ConnectionParms.py autobypass=True
        #    2) Start WebServer.py
        #    3) Make sure the json converter (java/run.sh) is running
        self.assertTrue(reduce(lambda x, y: x and self.doTest(y), urls, True))

    def testErrors(self):
        # TODO: the custom error code isn't part of the response.  The html is rxed via e.read(), but it takes work
        self.assertTrue(reduce(lambda x, y: x and self.doErrorTest(y[0], y[1]), errorurls, True))


if __name__ == "__main__":
    unittest.main()