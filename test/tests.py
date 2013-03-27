import os
import shutil
import unittest
import hashlib
from subprocess import call

args = None

def make_file(path, content):
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass

    with open(path, 'w') as file:
        file.write(content)

def destroy_repo(args):
    shutil.rmtree(args.local, True)
    shutil.rmtree(args.remote, True)

def init_repo(args, objects):
    destroy_repo(args)

    call(['git', 'init', '-q', args.local])

    origwd = os.getcwd()
    os.chdir(args.local)

    call(['git', 'config', 'filter.exile.clean', 'exile-clean %f'])
    call(['git', 'config', 'filter.exile.smudge', 'exile-smudge'])
    call(['git', 'config', 'exile-repo.test.get', 'cp %s/$REMOTE $LOCAL' % (args.remote)])
    call(['git', 'config', 'exile-repo.test.put', 'cp $LOCAL %s/$REMOTE' % (args.remote)])

    make_file('.gitattributes', '*.txt filter=exile repo=test')
    for object in objects:
        make_file(object.path, object.contents)

    os.chdir(origwd)
    os.mkdir(args.remote)

def commit_and_push(path='.'):
    call(['git', 'add', '.'])
    call(['git', 'commit', '-q', '-m', 'Test'])
    call(['git', 'exile', 'push', path])

class TestObject:
    def __init__(self, contents, path):
        hasher = hashlib.sha1()
        hasher.update(contents)
        hash = hasher.hexdigest()

        self.object = '.git/exile/test/' + hash
        self.hash = hash
        self.contents = contents
        self.path = path


    def assertFileValid(self, test, path, check_name=True):
        if check_name:
            test.assertEqual(os.path.basename(path), self.hash)

        test.assertTrue(os.path.exists(path))

        with open(path, 'r') as file:
            actual = file.read()
        test.assertEqual(actual, self.contents)

    def assertWorkingValid(self, test):
        self.assertFileValid(test, self.path, False)

    def assertLocalValid(self, test):
        self.assertFileValid(test, self.object)

    def assertRemoteValid(self, test):
        self.assertFileValid(test, test.args.remote + os.sep + self.hash)

    def assertWorkingMissing(self, test):
        test.assertFalse(os.path.exists(self.path))

    def assertLocalMissing(self, test):
        test.assertFalse(os.path.exists(self.object))

    def assertRemoteMissing(self, test):
        test.assertFalse(os.path.exists(test.args.remote + os.sep + self.hash))

class ExileTestCase(unittest.TestCase):
    files = [
        TestObject('test file 1', 'one.txt'),
        TestObject('test file 4', 'has space.txt'),
        TestObject('test file 2', 'sub/two.txt'),
        TestObject('test file 3', 'sub/dir/three.txt')
    ]

    def setUp(self):
        global args
        print ''  # separate test output
        self.files = ExileTestCase.files
        self.args = args
        init_repo(args, self.files)
        self.origwd = os.getcwd()
        os.chdir(args.local)

    def tearDown(self):
        os.chdir(self.origwd)
        destroy_repo(self.args)
       
    def test_add(self):
        call(['git', 'add', '.'])
        for file in self.files:
            file.assertLocalValid(self)

    def test_push(self):
        commit_and_push()
        for file in self.files:
            file.assertRemoteValid(self)

    def test_pull(self):
        commit_and_push()
        for file in self.files:
            os.remove(file.object)
            os.remove(file.path)

        call(['git', 'checkout', '.'])
        call(['git', 'exile', 'pull', '.'])
        for file in self.files:
            file.assertLocalValid(self)
            file.assertWorkingValid(self)

    def test_pull_clean(self):
        commit_and_push()
        for file in self.files:
            os.remove(file.path)
        shutil.rmtree('.git/exile')

        call(['git', 'checkout', '.'])
        call(['git', 'exile', 'pull', '.'])
        for file in self.files:
            file.assertLocalValid(self)
            file.assertWorkingValid(self)

    def test_pull_working(self):
        commit_and_push()
        for file in self.files:
            os.remove(file.object)
            os.remove(file.path)

        call(['git', 'exile', 'pull', '.'])
        for file in self.files:
            file.assertLocalValid(self)
            file.assertWorkingValid(self)

    def test_pull_subdir(self):
        commit_and_push()
        for file in self.files:
            os.remove(file.object)
            os.remove(file.path)

        os.chdir('sub')
        call(['git', 'exile', 'pull', '.'])
        os.chdir('..')

        self.files[0].assertLocalMissing(self)
        self.files[0].assertWorkingMissing(self)
        # TODO: maybe arrange self.files by directory to avoid using indicies
        for file in self.files[2:]:
            file.assertLocalValid(self)
            file.assertWorkingValid(self)

    def test_push_subdir(self):
        commit_and_push('sub')

        self.files[0].assertRemoteMissing(self)
        for file in self.files[2:]:
            file.assertRemoteValid(self)

    def test_repair(self):
        commit_and_push()

        with open(self.files[0].object, 'w') as file:
            file.write('')
        
        call(['git', 'exile', 'repair']) 

        for file in self.files:
            file.assertLocalValid(self)

    def test_push_corrupt(self):
        commit_and_push()

        with open(self.files[0].object, 'w') as file:
            file.write('')

        call(['git', 'exile', 'push', '.'])
        for file in self.files:
            file.assertRemoteValid(self)
