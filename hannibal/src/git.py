import os, path
from config import gitcmd
from utils import log, simple_exec

def has_correct_origin(name, parent, origin):
    '''Does the git repository located at "parent/name" have an upstream origin
    of "origin"?

    name, parent are assumed to be "path" objects
    '''
    repo = parent / name
    cmd = "%s config --get remote.origin.url" % gitcmd
    pid, retcode, stdout, stderr = simple_exec(cmd, repo)
    return retcode == 0 and stdout.startswith(origin)

def clone(name, parent, origin):
    '''Perform a git clone of "origin" into "parent/name".

    Anything that *was* in "parent/name" is nuked. The clone operation doesn't
    take standard input, so whatever git transport you use should support
    password-less operation.

    name, parent are assumed to be "path" objects
    '''
    if not parent.exists(): parent.makedirs()
    repo = parent / name
    if repo.exists(): 
        log("Nuking existing repo in %s" % repo)
        repo.rmtree()
    cmd = "%s clone %s %s" % (gitcmd, origin, name)
    pid, retcode, stdout, stderr = simple_exec(cmd, parent)
    if retcode != 0:
        raise RuntimeError("Error cloning repo: " + stderr)

def dogit(name, parent, cmd):
    '''Perform git command "cmd" in "parent/name"

    cmd => something like "pull" or "reset --hard"
    '''
    repo = parent / name
    cmd = "%s %s" % (gitcmd, cmd)
    pid, retcode, stdout, stderr = simple_exec(cmd, repo)
    if retcode != 0:
        raise RuntimeError("Error with %s: %s" % (cmd, stderr))

def pull(name, parent):
    '''Perform the equivalent of a "git pull" in "parent/name".

    Under the hood, we do a "git fetch" followed by a hard reset to FETCH_HEAD.
    This prevents git from trying to merge into the local master branch.
    '''
    dogit(name, parent, "fetch")
    dogit(name, parent, "reset --hard FETCH_HEAD")
    dogit(name, parent, "clean -d -f -x")
