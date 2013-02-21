# git-exile

git-exile aims to provide another option for dealing with binary files in Git. It was inspired by [git-bin](https://github.com/Mighty-M/git-bin), and similarly uses smudge and clean filters to prevent binary files from being checked in to the repository.

The primary features of git-exile include:
 - track binary files just like any others (just `git add`)
 - only a small text file is actually checked in
 - configure any number of external repositories where your exiled files actually reside
 - pull down any subset of your files when you need then (no download at checkout-time)

## How it works

git-exile leverages git's [clean and smudge filter](http://www.kernel.org/pub/software/scm/git/docs/gitattributes.html) functionality to intercept binary files before they are added to the index and replace them with a small text file that tells us where the files actually reside. You can then store your files on some external datastore (like S3, another computer, or just a central location on your machine) and only pull them down when you need them. This keeps your repository small and fast, yet still allows you to track the revisions of your binary files using all the power that git offers.

## Configuration

There are two main components of configuration that git-exile relies on: some git configuration and `.gitattributes` files.

There is a script in the project root that serves as a template for configuring git-exile for your project. There are three things you need to do:
 - add the git-exile commands to your PATH
 - set up the clean and smudge filters (handled by `configure.sh`)
 - add an external repository

### Repositories

There are examples for some repository configurations in `configure.sh`, but all you need to do to define a repository is to tell git-exile how to get things from it and put things to it:

    git config exile-repo.example.get 'aws get my-bucket/$REMOTE $LOCAL'
    git config exile-repo.example.put 'aws put my-bucket/$REMOTE $LOCAL'

This defines a repository named "example", which is backed in S3 (the aws script used above can be found [here](http://s3.amazonaws.com/doc/s3-example-code/s3-curl.zip)). `REMOTE` and `LOCAL` are environment variables defined by git-exile to represent the file names on the remote and local hosts.

In the git fashion, git-exile stores files as objects identified by an SHA-1 hash, and so will store files on the remote repository in a flat structure with each object having its hash as its name.

### Attributes

Lastly, you will need to add some `.gitattributes` files to tell git-exile which files to filter out. You will need to specify two attributes on files for git-exile to process them. For example:

    *.png filter=exile repo=example

This will cause all files ending in ".png" to be processed by git-exile and the objects to associated with the repository named "images" (configured earlier).

You can read more about how `.gitattributes` files work [here](http://www.kernel.org/pub/software/scm/git/docs/gitattributes.html).

## Usage

Once you have git-exile configured, usage is fairly straightforward. Files will be automatically handled according to your `.gitattributes` configuration, so you can `add`, `commit`, `push`, etc as normal. When you add files to git, git-exile stores the real content in the `.git/exile` folder and uses the data there to silently replace references with the real file contents when needed. The only time you need to deal with git-exile is when you need objects that you don't have (maybe someone changed something or you just cloned a new repository) or you want to push your local objects to the remote repository. The commands you will use to do this are simply `pull` and `push`.

### `pull`

pull is used to update the files managed by git-exile in some sub-tree of your project. A simple example is just:

    git exile pull .

This will look for unresolved exiled file references in the current directory and all subdirectories and download the objects necessary to resolve the reference to its real content.

### `push`

push is used to push your local objects to the remote repository. It works similarly to pull, but instead pushes the appropriate objects to the remote repository. For example:

    git exile push .

This will look for exiled files in the current directory and all subdirectories, and push the objects corresponding to the current version to the remote repository.
