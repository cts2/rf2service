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

import requests
import argparse
import sys


def stub(opts):
    print("%s not implemented" % opts.action)
    return False


def genurl(opts, base=''):
    return (opts.url + ('/changeset/%s' % opts.changeset) + base + '?format=json') + \
           ('&description=%s' % opts.description if opts.description else '') + \
           ('&owner=%s' % opts.owner if opts.owner else '')

def checkerror(data):
    if not data.ok:
        print("Error %s: %s" % (data.status_code, data.reason))
    return not data.ok


def new(opts):
    data = requests.post(genurl(opts))
    if not checkerror(data):
        print('Changeset %s created' % data.json()['ChangeSetReferenceSetEntry']['referencedComponentId']['uuid'])
    return data.ok


def rollback(opts):
    data = requests.delete(genurl(opts))
    if not checkerror(data):
        print('Changeset %s was removed' % opts.changeset)
    return data.ok


def commit(opts):
    data = requests.put(genurl(opts, '/commit'))
    if not checkerror(data):
        print('Changeset %s was committed' % opts.changeset)
    return data.ok


def update(opts):
    data = requests.put(genurl(opts))
    if not checkerror(data):
        print('Changeset %s was updated' % opts.changeset)
    return data.ok

choices = {'new': new, 'update': update, 'commit': commit, 'rollback': rollback, 'list': stub}

def main(args):
    parser = argparse.ArgumentParser(description="RF2 Changeset Manager")
    parser.add_argument('-u', '--url', help="Base service URL", required=True)
    parser.add_argument('action', choices=choices.keys())
    parser.add_argument('changeset', help="Reference set name")
    parser.add_argument('-d', '--description', help="Reference set description")
    parser.add_argument('-o', '--owner', help="Reference set owner")
    opts = parser.parse_args(args)
    if opts.action != 'list' and not opts.changeset:
        print("Changeset name must be supplied")
        exit(0)
    return choices[opts.action](opts)




if __name__ == '__main__':
    main(sys.argv[1:])
