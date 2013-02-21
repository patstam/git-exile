import os
import string
import subprocess

header = 'GitExileReference'

class GitConfigCommand:
    def __init__(self, repo, action):
        cmd = subprocess.check_output(['git', 'config', 'exile-repo.%s.%s' % (repo, action)])
        self.template = string.Template(cmd.strip())
        self.repo = repo
        self.action = action
   
    def eval(self, vars):
        try:
            final = self.template.substitute(vars)
        except KeyError as e:
            print "Undefined variable '%s'. Valid variables for '%s' are:" % (e.args[0], self.action)
            for key in vars:
                print key
            return ''

        if len(final) is 0:
            print "No %s command configured for repository %s." % (self.action, self.repo)
            print "Configure it by setting exile-repo.%s.%s" % (self.repo, self.action)
        else:
            subprocess.call(final, shell=True)

def rootDir():
    gitroot = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip()
    return gitroot + os.sep + '.git/exile'

def hashObject(path):
    return subprocess.check_output(['shasum', '-a1', path]).split()[0]

def forEachSubtree(paths, callback):
    if len(paths) is 0: 
        print "No paths specified."
        return

    try:
        for file in subprocess.check_output(['git', 'ls-files', '--error-unmatch'] + paths).split():
            filter = subprocess.check_output(['git', 'check-attr', 'filter', file]).split()[2]
            if filter == 'exile':
                callback(file)
    except subprocess.CalledProcessError:
        pass    # called process should print appropriate message

def repoFor(path):
    return subprocess.check_output(['git', 'check-attr', 'repo', path]).split()[2]

def configuredRepositories():
    lines = subprocess.check_output(['git', 'config', '--get-regexp', 'exile-repo.*.*']).splitlines()
    return set(line.split()[0].split('.')[1] for line in lines)

def get(repo, hash):
    vars = { 'REMOTE': hash, 'LOCAL': rootDir() + os.sep + repo + os.sep + hash }
    GitConfigCommand(repo, 'get').eval(vars)

def isReference(path):
    with open(path, 'r') as data:
        magic = data.read(len(header))
    return magic == header
