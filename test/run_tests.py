#!/usr/bin/python

import os
import sys
import argparse
import unittest

import tests
from tests import ExileTestCase

parser = argparse.ArgumentParser(description="An automated test utility for git-exile. Tests in a temporary Git repository configured with a local 'remote' (get and put via 'cp').", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-l', '--local', default='/tmp/git-exile-local', help='path at which the Git repository will be created')
parser.add_argument('-r', '--remote', default='/tmp/git-exile-remote', help='path at which the remote repository will be created')
parser.add_argument('-e', '--exile', default='../bin', help='location of the git-exile executables to test')
args = parser.parse_args()

os.environ['PATH'] = os.path.abspath(args.exile) + os.pathsep + os.environ['PATH']

args.local = os.path.abspath(args.local)
args.remote = os.path.abspath(args.remote)
tests.args = args

#TODO: pass args properly to unittest
sys.argv = sys.argv[:1]
unittest.main()
