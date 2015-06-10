# -*- coding: utf-8 -*-
# Copyright (c) 2015, Mayo Clinic
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
import itertools
import re
import os
import sys
from fuzzywuzzy import fuzz

_curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.append(os.path.join(_curdir, '..', '..', 'rf2db'))

from ConfigManager. import ConfigManager
ConfigManager.set_configfile(os.path.join(_curdir, '..', '..', 'rf2service', 'settings.conf'))


from rf2db.db.RF2DescriptionTextFile import DescriptionTextDB, description_match_parms
from rf2db.db.RF2PnAndFSN import PNandFSNDB
from rf2db.db.RF2TransitiveClosure import TransitiveClosureDB
db = DescriptionTextDB()
pnfsndb = PNandFSNDB()
tcdb = TransitiveClosureDB()




class tr_entry(object):
    """ Term ratio object. Carries the matching term
    """
    def __init__(self, term, ratio, c_ratio):
        self.term = term
        self.ratio = ratio
        self.c_ratio = c_ratio

""" conceptId / max ratio / trEntryList object """
class conc_entry(object):
    def __init__(self, kg):
        k, g = kg
        ctr = list(g)    # g is volatile, so we have to turn it into a list
        self.conceptId = k
        self.ratio = reduce(lambda a, ctr: a if a > ctr[2] else ctr[2], ctr, 0)
        self.trlist = map(lambda (_, t, r, c_r) : tr_entry(t,r, c_r), sorted(ctr, key=lambda e:e[2], reverse=True))

    @property
    def pn(self):
        return pnfsndb.getpn(self.conceptId)

    @property
    def fsn(self):
        return pnfsndb.getfsn(self.conceptId)



def uniqueConcepts(termlist):
    """
    Return a list of conc_entries from a matching term list
    @param termlist: iterator of the triple (conceptId, term, ratio)
    @return: ordered list of conc_entries in decreasing ratio order
    """
    keyf = lambda e: e[0]
    return sorted(map(conc_entry, itertools.groupby(sorted(termlist, key=keyf), keyf)),
                      key=lambda ce: ce.ratio, reverse=True)



def procrow(row, opts):

    def rowFilter(e):
        if e[2] < opts.cutoff or int(e[0]) == opts.genus:
            return False
        if opts.trees:
            for tree in opts.trees:
                if tree != int(e[0]):    # Don't pass the root -- it often qualifies
                    if tcdb.are_related(tree, e[0]):
                        return True
            return False
        return True

    if len(row) < opts.matchcolumn or not row[opts.matchcolumn-1].strip():
        col = None
    else:
        col = row[opts.matchcolumn-1]
    ucs = []

    # Grab a genus if one is there
    if opts.genuscol and len(row) >= opts.genuscol and row[opts.genuscol-1].strip():
        opts.genus = int(row[opts.genuscol-1].strip())

    # Isolate any tree info
    if opts.treecol and len(row) >= opts.treecol:
        tc = row[opts.treecol-1].strip()
        if tc:
            if not tc.startswith(':'):
                opts.trees = []
            else:
                tc = tc[1:]
            opts.trees.append(int(tc))

    if col and (not opts.trees or opts.trees[0] != 0):
        # Step 1: search for the entire match term
        rtns = filter(rowFilter,
                      map(lambda r: (r.conceptId, r.term, fuzz.ratio(r.term, col), fuzz.ratio(r.term, col)),
                      db.getDescriptions_p([col], matchalgorithm=opts.matchalgorithm, maxtoreturn=10000)))

        if not opts.nw:
            # Step 2: Cut into words and search for the list of words
            vals = filter(lambda e: e, col.replace('[/-:()"]',' ').split(' '))
            rtns += filter(rowFilter,
                           map(lambda r: (r.conceptId, r.term, fuzz.ratio(r.term, col), fuzz.ratio(r.term, col)),
                           db.getDescriptions_p(vals, matchalgorithm='wordstart', maxtoreturn=10000)))

            # Step 3: Cut into chunks based on delimiters and try to match each chunk
            vals = filter(lambda e: e, re.sub(r'[/-:]','~',col).split('~'))
            for v in vals:
                rtns += filter(rowFilter,
                               map(lambda r: (r.conceptId, r.term, fuzz.ratio(r.term, v), fuzz.ratio(r.term, col)),
                               db.getDescriptions_p(v, matchalgorithm='contains', maxtoreturn=10000)))

            # Step 3: Cut into words and search for each word, but ratio goes against individual item
            vals = filter(lambda e: e, re.sub(r'[/-:()"]',' ',col).split(' '))
            for v in vals:
                rtns += filter(rowFilter,
                               map(lambda r: (r.conceptId, r.term, fuzz.ratio(r.term, v), fuzz.ratio(r.term, col)),
                               db.getDescriptions_p(v, matchalgorithm='contains', maxtoreturn=10000)))

        ucs = uniqueConcepts(set(rtns))
    printrow(row,opts,ucs[0] if len(ucs) else None)
    [printrow([],opts,uc) for uc in ucs[1:opts.maxmatches]]

col_header = ['SCTID', 'FSN/DESIG', 'R_RATIO', 'C_RATIO']

def printrow(row, opts, unique_concepts=None, header=None):
    """ Supply all of the candidate concepts that matched.   Format:
        C1   C2    C3    ... match_column SCTID FSN          highest_ratio ___       match_column+1, ...
        __   __    __             ___      ___  designation  r_ratioo      c_ratio
    @param row: row that matched. Can be empty if not to be repeated
    @param opts: carries delimiter, outputc column
    @param unique_concepts: C{Conc_Entry} entry
    """
    if not header:
        header = ['','','','']
    row.extend([''] * max(opts.outputcolumn - len(row) - 1,0))
    if not unique_concepts:
        print opts.delimiter.join(row[0:opts.outputcolumn-1] + header + row[opts.outputcolumn-1:])
    else:
        row.insert(opts.outputcolumn-1, str(unique_concepts.conceptId))
        row.insert(opts.outputcolumn, unique_concepts.fsn.encode('utf-8'))
        row.insert(opts.outputcolumn+1, str(unique_concepts.ratio))
        row.insert(opts.outputcolumn+2, '')
        print opts.delimiter.join(row)
        if not opts.nosyn:
            for tr in unique_concepts.trlist:
                print opts.delimiter.join(([''] * opts.outputcolumn) + [tr.term.encode('utf-8'), str(tr.ratio), str(tr.c_ratio)])


def main():
    parser = argparse.ArgumentParser(description="Text match operation")
    parser.add_argument('infile', help="Input text file")
    parser.add_argument('-a', '--matchalgorithm', help="match algorithm", choices=description_match_parms.matchalgorithm.possibleValues(), default='contains')
    parser.add_argument('-c', '--matchcolumn', metavar="Column to match", help="Text column to match (1 based)", type=int, default=1)
    parser.add_argument('-d', '--delimiter', metavar="delimiter", help="Delimiter", default="\t")
    parser.add_argument('-f', '--firstrow', metavar="first row", help="First row with data (1 based)", type=int, default=2)
    parser.add_argument('-l', '--literal', help="input is actual text", action="store_true")
    parser.add_argument('-m', '--maxmatches', metavar="maximum matches to return", type=int, help="Number of matches to return", default=5)
    parser.add_argument('-n', '--nrows', metavar="number of rows", type=int, help="Number of rows to evaluate")
    parser.add_argument('-o', '--outputcolumn', metavar="Output column", help="Column for output (1 based). Default - matchcolumn + 1", type=int)
    parser.add_argument('-t', '--tree', metavar="restrict search to branch", type=int, help="SCTID of branch")
    parser.add_argument('--nosyn', help="no synonyms", action="store_true")
    parser.add_argument('--treecol', metavar="tree column", type=int, help="Column with SCTID tree(s)")
    parser.add_argument('--cutoff', metavar="ratio cutoff", type=int, help="Fuzz ratio cutoff", default=75)
    parser.add_argument('--genuscol', metavar="genus column", type=int, help="Genus column - don't pass this as a match")
    parser.add_argument('--nw', help="Don't do the word by word search", action="store_true")

    opts = parser.parse_args()
    opts.trees = [opts.tree] if opts.tree else []
    opts.genus = None
    if opts.literal:
        opts.matchcolumn = 1
        opts.outputcolumn = 2
        procrow([opts.infile], opts)
    else:
        if not opts.outputcolumn:
            opts.outputcolumn = opts.matchcolumn + 1
        with open(opts.infile, 'rU') as csvfile:
            reader = csv.reader(csvfile, delimiter=opts.delimiter)
            if opts.firstrow > 1:
                printrow(reader.next(),opts,header=col_header)
            zip(range(2, opts.firstrow), (printrow(row, opts) for row in reader))  # Skip nrows rows
            zip((procrow(row, opts) for row in reader), range(1, opts.nrows)) if opts.nrows else \
                [procrow(row, opts) for row in reader]
            [printrow(row, opts,[]) for row in reader]

if __name__ == '__main__':
    main()

