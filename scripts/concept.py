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
import os
import requests
import argparse
import sys

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.append(os.path.join(_curdir, '..', '..', 'rf2db'))

def stub(opts):
    print("%s not implemented" % opts.action)
    return False


def genurl(opts, base=''):
    return (opts.url + '/concept' + base + '?format=json') + \
           ('&term=%s' % opts.term if opts.term else '') + \
           ('&=%s' % opts.owner if opts.owner else '')


def checkerror(data):
    if not data.ok:
        print("Error %s: %s" % (data.status_code, data.reason))
    return not data.ok


def make_it_so(f, url):
    return f(url+'&bypass=1')


def cs_name_to_id(opts):
    url = opts.url + '/changeset/' + opts.changeset + '?format=json'
    data = make_it_so(requests.get, url)
    if checkerror(data):
        return data.ok
    return data.json()['ChangeSetReferenceSetEntry']['referencedComponentId']['uuid']


def new(opts):
    """ Add a new concept
    :param opts: opts.term = preferred name, opts.parent = parent sctid
    :return: pass/fail
    """
    url = opts.url + '/concept/' + str(opts.parent) + '/base?format=json&changeset=' + opts.changeset
    data = make_it_so(requests.get, url)
    if checkerror(data):
        return data.ok
    fsn = opts.term + ' ' + data.json()['val']
    url = opts.url + '/concept/' + str(opts.parent) + '/fsn?format=json&changeset=' + opts.changeset
    data = make_it_so(requests.get, url)
    if checkerror(data):
        return data.ok
    parent_fsn = data.json()['Description']['term']

    url = opts.url + '/concept?format=json&changeset=' + opts.changeset
    data = make_it_so(requests.post, url)
    if not checkerror(data):
        conceptid = data.json()['Concept']['id']
        print('Concept id %s was created' % conceptid)
    else:
        return data.ok

    url = opts.url + '/description?format=json&changeset=%s&concept=%s&term=%s' % (opts.changeset, conceptid, opts.term)
    data = make_it_so(requests.post, url)
    if not checkerror(data):
        descid = data.json()['Description']['id']
        print("Description id %s was created for prefered name '%s'" % (descid, opts.term))
    else:
        return data.ok

    url = opts.url + '/description?format=json&type=%s&changeset=%s&concept=%s&term=%s' % \
                     ('f', opts.changeset, conceptid, fsn)
    data = make_it_so(requests.post, url)
    if not checkerror(data):
        descid = data.json()['Description']['id']
        print("Description id %s was created for fsn '%s'" % (descid, fsn))
    else:
        return data.ok

    url = opts.url + '/relationship/source/%s/target/%s?format=json&changeset=%s' % \
                     (conceptid, opts.parent, opts.changeset)
    data = make_it_so(requests.post, url)
    if not checkerror(data):
        relid = data.json()['Relationship']['id']
        print('Relationship id %s was created (%s is_a %s)' % (relid, fsn, parent_fsn))
    return data.ok

choices = {'new': new, 'update': stub, 'delete': stub}


def main(args):
    parser = argparse.ArgumentParser(description="RF2 Concept Manager")
    parser.add_argument('-u', '--url', help="Base service URL")
    parser.add_argument('action', choices=choices.keys())
    parser.add_argument('changeset', help="Changeset name")
    parser.add_argument('-t', '--term', help="Preferred name")
    parser.add_argument('-p', '--parent', help="Parent concept", type=int)
    opts = parser.parse_args(args)
    return choices[opts.action](opts)


if __name__ == '__main__':
    main(sys.argv[1:])
