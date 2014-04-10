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
import argparse
import csv
import uuid

from config.ConfigManager import ConfigManager
from rf2db.db.RF2FileCommon import config_parms
from rf2db.db.RF2ComplexMapFile import ComplexMapDB
from rf2db.utils.sctid import sctid


chunksize = 1000    # number of records to add per write
effectiveTime = '20140310'
entries = []

def procrow(row, opts):
    entries.append([str(uuid.uuid4()), effectiveTime, 1, opts.moduleId, opts.refsetId, row[3], 1, 1, row[1]])


def writeblock(tc, db, tbl):
    insertList = ["('%s', '%s', %s, %s, %s, %s, %s, %s, '%s')" % tuple(e) for e in tc]
    db.execute("INSERT INTO %s (id, effectiveTime, active, moduleid, refsetid, referencedComponentId, mapGroup, mapPriority, mapTarget) VALUES " % tbl + ','.join(insertList) )
    db.commit()


def main():
    cfg = ConfigManager(config_parms)
    parser = argparse.ArgumentParser(description="Load Trillium Bridge map into RF2 ComplexMap file")
    parser.add_argument('configfile', help="Configuration file location")
    parser.add_argument('infile', help="Input TSV file")
    parser.add_argument('-f', '--firstrow', metavar="first row", help="First row with data (1 based)", type=int, default=2)
    parser.add_argument('-m', '--moduleId', type=int, help="Module Identifier", required=True)
    parser.add_argument('-r', '--refsetId', type=int, help="Refset Identifier", required=True)

    opts = parser.parse_args()

    cfg.set_configfile(opts.configfile)

    # Throws assertionError if the id isn't valid
    mid = sctid(opts.moduleId)
    rid = sctid(opts.refsetId)

    with open(opts.infile, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        zip(range(1, opts.firstrow), reader)          # Skip nrows rows
        [procrow(row, opts) for row in reader]

    if entries:
        print("Writing records to table")
        db = ComplexMapDB()
        for s in range(0, len(entries), 1000):
            writeblock(entries[s:s+chunksize], db.connect(), db._tname(True))


if __name__ == '__main__':
    main()