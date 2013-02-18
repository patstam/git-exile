#!/usr/bin/python

import sys
import os
import subprocess
import string

bindir = '.git/exile'
header = 'GitExileReference'

for file in subprocess.check_output('git ls-files ' + ' '.join(sys.argv[1:]), shell=True).split():
    filter = subprocess.check_output('git check-attr filter ' + file, shell=True).split()[2]
    if filter == 'exile':
        with open(file, 'r') as data:
            magic = data.read(len(header))
        if magic == header:
            with open(file, 'r') as data:
                location = data.readlines()[1].strip().split('/')
            repo = location[0]
            hash = location[1]
            blob = bindir + os.sep + repo + os.sep + hash
            if not os.path.exists(blob):
                print 'exile: pulling %s from %s' % (hash, repo)
                vars = { 'SRC': hash, 'DEST': blob }
                cmd = subprocess.check_output('git config exile-repo.' + repo + '.get', shell=True)
                template = string.Template(cmd.strip())
                subprocess.call(template.substitute(vars), shell=True)
            print 'exile: refreshing ' + file
            os.remove(file)
            subprocess.call('git checkout ' + file, shell=True)
