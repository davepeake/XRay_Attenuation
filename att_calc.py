#!/usr/bin/python

from optparse import OptionParser

import nistxcom as nx

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-m','--mat', dest='mat_file', help='Save results a matlab file')
    parser.add_option('-e','--element', 
