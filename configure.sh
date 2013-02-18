#!/bin/bash -e

echo 'This script contains documentation on configuring git-exile. See the source for details.'

# Any arguments passed to this script are forwarded to git config. (ie: --global)

# Configure repositories
#
# A repository is declared as "exile-repo.<reponame>" and has two parameters:
#   get - the command used to transfer a file from the remote to this machine
#   put - the command used to transfer a file from this machine to the remote
#
# Two special environment variables are defined for these commands:
#   REMOTE - the name of the file on the remote repository
#   LOCAL - the name of the file on the local host
# 
# Note that "get" is tasked with transfering REMOTE to LOCAL and "put"
# does the opposite.

# Example using S3
# 'aws' script available at:
# http://s3.amazonaws.com/doc/s3-example-code/s3-curl.zip
#git config $@ exile-repo.example.get 'aws get my-bucket/$REMOTE $LOCAL'
#git config $@ exile-repo.example.put 'aws put my-bucket/$REMOTE $LOCAL'

# Example using SCP
#git config $@ exile-repo.example.get 'scp repo.example.com:/exile/$REMOTE $LOCAL'
#git config $@ exile-repo.example.put 'scp $LOCAL repo.example.com:/exile/$REMOTE'

# Set up the clean and smudge filters, you shouldn't need to touch these
git config $@ filter.exile.clean "exile-clean %f"
git config $@ filter.exile.smudge "exile-smudge"

if [ -z "`which git-exile`" ]; then
    echo 'NOTE: git-exile does not appear to be on your PATH. The exile-* commands must be accessible on your path for git-exile to function.'
else
    echo 'git-exile is now ready to use!'
fi
