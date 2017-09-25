'''
Created on Sep 25, 2017

@author: louie
'''

import filecmp

from flashcardsquiz.quiz import QList

TWO_LINES = 'twolines.qz'
FIVE_LINES = 'fiveq.qz'
TMP_FILE = 'tmp.tmp'


def test_ctr():
    assert len(QList()) == 5


def test_ctr_2():
    assert len(QList(TWO_LINES)) == 2


def test_read_write():
    infile = FIVE_LINES
    outfile = TMP_FILE
    qlist = QList(infile)
    qlist.write(outfile)
    assert(filecmp.cmp(infile, outfile))


def test_read_write_extra_fields():
    '''
    Show that writing a file with non-default last 2 fields differs from the read in file

    The program currently ignores the last two fields, and
    overwrites them with default values.  
    '''
    infile = TWO_LINES
    outfile = TMP_FILE
    qlist = QList(infile)
    qlist.write(outfile)
    assert(filecmp.cmp(infile, outfile) == False)
