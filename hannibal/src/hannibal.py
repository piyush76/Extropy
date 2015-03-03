from __future__ import with_statement 
import sys, os, socket, time, shutil
from path import path

import json, config, commandline, webui, utils, git
from commandline import expose_to_shell
from utils import log, ensuregone

def init():
    '''Initialize hannibal's configuration, making sure directories and files
    exist and whatnot.
    '''
    dd, mf, bf, sf = config.datadir, config.manifests_file, config.bundles_file, config.servers_file
    if not dd.exists(): dd.makedirs()
    # Initialize datafiles
    for f in [mf, bf, sf]:
        if not f.exists():
            with f.open('w') as fd: fd.write(json.write({}))

def parse_dict(fname):
    '''Read a JSON dictionary from file "fname"
    '''
    with fname.open('r') as f: return json.read(f.read())

def dump_dict(d, fname):
    '''Serialize dictionary "d" as JSON, dumping it to file "fname"

    The write is atomic, meaning that "d" is serialized to a temporary file
    first and then moved into place.  This relies on the atomicity of a
    filesystem move.
    '''
    source = config.datadir / ("%s" % time.time())
    dest = fname
    with source.open('w') as f: f.write(json.write(d))
    shutil.move(str(source), str(dest))

def parse_manifests(): return parse_dict(config.manifests_file)
def dump_manifests(manifests): dump_dict(manifests, config.manifests_file)
def parse_bundles(): return parse_dict(config.bundles_file)
def dump_bundles(bundles): dump_dict(bundles, config.bundles_file)
def parse_servers(): return parse_dict(config.servers_file)
def dump_servers(servers): dump_dict(servers, config.servers_file)

def print_map(m):
    '''Print a formatted version of the supplied map to stdout
    '''
    for k, v in m.items(): print "%-20s %s" % (k, v)

def update_map(key, value, whichmap):
    '''Store a key=>value mapping in a particular map ("manifests", "bundles",
    "servers")
    '''
    if key in ["manifest", "modules"]:
        raise RuntimeError("That name is reserved. Try another one.")
    mod = sys.modules[__name__]
    loadfn = getattr(mod, "parse_"+whichmap)
    storefn = getattr(mod, "dump_"+whichmap)
    m = loadfn()
    m[key] = value
    storefn(m)

def remove_from_map(key, whichmap):
    '''Remove the given key from a particular map ("manifests", "bundles",
    "servers")
    '''
    mod = sys.modules[__name__]
    loadfn = getattr(mod, "parse_"+whichmap)
    storefn = getattr(mod, "dump_"+whichmap)
    m = loadfn()
    if key in m:
        del m[key]
        storefn(m)

def ensure_unused(key):
    '''Ensure that the specified key isn't actively used in a server
    profile (either as a manifest or a bundle)

    Thows an exception if the key is attached to a server.
    '''
    for server, md in parse_servers().iteritems():
        if key == md["manifest"] or key in md["bundles"]:
            raise RuntimeError("Server %s is using '%s'" % (server, key))

@expose_to_shell("list-manifests")
def list_manifests():
    '''List all available manifests
    '''
    print_map(parse_manifests())

@expose_to_shell("list-bundles")
def list_bundles():
    '''List all available bundles
    '''
    print_map(parse_bundles())

@expose_to_shell("add-manifest")
def add_manifest(name, git_uri):
    '''Add a new manifest, or modify existing

    name            The name of the new manifest. If a manifest by this name
                    already exists in hannibal's database, hannibal will
                    overwrite it.

    git_uri         A pathspec that, when passed to "git clone", will checkout
                    the sources for this manifest.

                    Examples:
                    ssh://user@host/path/to/manifest/dir/
                    /var/lib/git/repos/manifest/dir/
                    git://host/path/to/manifest/dir/
    '''
    update_map(name, git_uri, "manifests")

@expose_to_shell("remove-manifest")
def remove_manifest(name):
    '''Delete the given manifest from hannibal's database

    name            The name of the manifest hannibal should delete.
    '''
    ensure_unused(name)
    remove_from_map(name, "manifests")

@expose_to_shell("add-bundle")
def add_bundle(name, git_uri):
    '''Add a new bundle, or modify existing

    name            The name of the new bundle. If a bundle by this name
                    already exists in hannibal's database, hannibal will
                    overwrite it.

    git_uri         A pathspec that, when passed to "git clone", will checkout
                    the sources for this bundle.

                    Examples:
                    ssh://user@host/path/to/bundle/dir/
                    /var/lib/git/repos/bundle/dir/
                    git://host/path/to/bundle/dir/
    '''
    update_map(name, git_uri, "bundles")

@expose_to_shell("remove-bundle")
def remove_bundle(name):
    '''Delete the given bundle from hannibal's database

    name            The name of the bundle hannibal should delete.
    '''
    ensure_unused(name)
    remove_from_map(name, "bundles")

@expose_to_shell("list-servers")
def list_servers():
    '''List all the puppetmaster servers that hannibal knows about
    '''
    print_map(parse_servers())

@expose_to_shell("remove-server")
def remove_server(server):
    '''Delete a server's hannibal profile
    '''
    remove_from_map(server, "servers")

@expose_to_shell("profile")
def profile(server):
    '''List the manifest and bundles associated with a server

    Bundles are displayed in priority order with the highest priority bundle
    appearing first.

    server          The name of the server to query
    '''
    servers = parse_servers()
    if server in servers:
        profile = servers[server]
        manifest, bundles = profile["manifest"], profile["bundles"]
        print "MANIFEST:"
        print manifest
        print "BUNDLES:"
        for bundle in bundles: print bundle

@expose_to_shell("mod-profile")
def modify_profile(server):
    '''Alter the configuration profile of a server

    Hannibal will read a new configuration profile from stdin and associate it
    with "server". If "server" already has a configuration stored in hannibal's
    database, then hannibal will overwrite it.

    The input format is the same as the output format used by "hannibal profile".

    Example input:
    MANIFEST:
    some-manifest-name
    BUNDLES:
    name-of-bundle-1
    name-of-bundle-2
    name-of-bundle-3

    server          The name of the server whose configuration you wish to 
                    update
    '''
    input = sys.stdin.read().splitlines()
    if input[0] != "MANIFEST:" or input[2] != "BUNDLES:":
        raise RuntimeError("Your input data is malformed.")
    m = input[1]
    bs = input[3:]

    if m in bs:
        raise RuntimeError("Names must be unique across manifests, and bundles")

    manifests, bundles = parse_manifests(), parse_bundles()
    if m not in manifests:
        raise RuntimeError("%s isn't a manifest I know about." % repr(m))
    for b in bs:
        if b not in bundles:
            raise RuntimeError("%s isn't a bundle I know about." % repr(b))

    servers = parse_servers()
    servers[server] = {"manifest": m, "bundles": bs}
    dump_servers(servers)

@expose_to_shell("dump-db")
def dump_database():
    '''Serialize hannibal's database to stdout (useful for backup)
    '''
    db = {"manifests": parse_manifests(), "bundles": parse_bundles(), "servers": parse_servers()}
    print json.write(db)

@expose_to_shell("slurp-db")
def slurp_database():
    '''Reinitialize hannibal's db with information from stdin.

    Hannibal expects the input to be from a prior run of "dump-db". Error
    checking is limited, so use this at your own risk. But if you just run it
    using the output of "dump-db", and not on some JSON you made up one day
    then you should be fine.
    '''
    input = sys.stdin.read()
    db = json.read(input)
    for key in ["manifests", "bundles", "servers"]:
        if key not in db:
            raise RuntimeError("Missing database store: %s" % key)
    dump_manifests(db["manifests"])
    dump_bundles(db["bundles"])
    dump_servers(db["servers"])


@expose_to_shell("http-serve")
def serve(port):
    '''Serve up configuration profiles via HTTP

    port            Which port to listen on for connections
    '''
    webui.serve_forever(port)

@expose_to_shell("sync")
def sync(hannibal_server, port):
    '''Download the requisite manifest and bundles to this machine

    First, we'll ask "hannibal_server:port" for the configuration profile of
    this machine (the machine name is queried via the "gethostname" syscall,
    and should be the same as that returned by running the "hostname" command).
    
    "hannibal_server" and "port" should point to an instance of hannibal that
    was launched using "hannibal http-serve".

    We then do a "git clone" of our manifest and bundles into this directory.
    If there's already a git repo in "local_path" for a manifest or bundle, we
    do a "git pull" followed by a "git reset --hard". This will ensure that
    we've got the latest version of everything this machine needs.

    hannibal_server     Name of machine running "hannibal http-serve"

    port                Port that "hannibal_server" is listening on
    '''
    metadata = utils.jsonrpc(hannibal_server, port, "/profile/%s" % socket.gethostname())
    lp = path(config.local_path)
    repos = [("manifest", metadata["manifest"]["git-uri"])]
    repos.extend([(b["name"], b["git-uri"]) for b in metadata["bundles"]])
    for name, uri in repos:
        if not (lp / name).isdir() or not git.has_correct_origin(name, lp, uri):
            git.clone(name, lp, uri)
        else:
            try:
                git.pull(name, lp)
            except RuntimeError, e:
                # Error during pull. Let's just nuke the directory any do a clone.
                (lp / name).rmtree()
                git.clone(name, lp, uri)

    # Remove directories that aren't involved in the sync
    names = dict(repos).keys() + ["modules"]
    for dir in lp.dirs():
        if dir.basename() not in names:
            log("%s is stale, nuking" % dir)
            dir.rmtree()

    # Build symlink farm for puppet's modulepath
    start = time.time()
    modules = lp / "modules"
    ensuregone(modules)
    modules.makedirs()
    for b in metadata["bundles"]:
        name = b["name"]
        bundlepath = lp / name
        for module in bundlepath.dirs():
            newlink = modules / module.basename()
            pointsto = bundlepath / module.basename()
            if newlink.exists(): continue
            pointsto.symlink(newlink)
    finish = time.time()
    log("Link farm rebuilt in %.3f seconds" % (finish-start))

    # Dump out the list of bundle name, in order. This machine can use this to
    # do ordering-dependent operations for bundles.
    with open(lp / "ordering.txt", 'w') as f:
        for b in metadata["bundles"]:
            f.write(b["name"])
            f.write('\n')

@expose_to_shell("make-client")
def bootstrap_client(puppetmaster):
    '''Do an initial puppet-based bootstrap of this box

    puppetmaster    Name of the puppetmaster machine that manages this box
    '''
    log("Attempting puppet connection...")
    fullcmd = 'puppetd -t --no-noop --pluginsync --plugindest=/var/lib/puppet/plugins --libdir=/var/lib/puppet/plugins --server %(puppetmaster)s'
    shortcmd = 'puppetd -t --no-noop'
    for i in range(4):
        os.system(fullcmd % {'puppetmaster': puppetmaster})
    os.system(shortcmd)

@expose_to_shell("make-master")
def bootstrap(hannibal_server, port):
    '''Turn this box into a puppetmaster.

    We will:
    1) Do a "hannibal sync" against the server specified in the argument list
    2) Run "puppet" several times to configure itself as a puppetmaster
    3) Run "puppetd -t" to verify connectivity to the master and normal
    puppet operation.

    All of the commands executed during bootstrap have their output echoed to
    the terminal window, so the entire operation should be pretty transparent.

    hannibal_server     Name of machine running "hannibal http-serve"

    port                Port that "hannibal_server" is listening on
    '''
    log("Syncing via hannibal...")
    sync(hannibal_server, port)

    # Run puppet to build the puppetmaster. We need to do this a few times,
    # to ensure that all dependcies have been sorted out
    cmd = "puppet -v --use-nodes --modulepath %s:%s --libdir=%s --no-pluginsync %s" % (config.manifest_dir, config.modules_dir, config.plugin_dir, config.manifest_dir / "site.pp")
    for i in range(4):
        log(cmd)
        os.system(cmd)

    # FIXME: This should move into the puppet manifest for mongrel/rails...
    cmd = "chown -R puppet:puppet /var/log/puppet"
    log(cmd)
    os.system(cmd)

    # Now the puppetmaster should be up an running (fingers crossed!)
    # Let's run puppet the typical way.
    cmd = "puppetd -t"
    for i in range(4):
        log(cmd)
        os.system(cmd)

    log("Done")


def main():
    cli = commandline.build(globals())
    # Is this a bogus command, or was no command given?
    if len(sys.argv) == 1 or (sys.argv[1] != "help" and sys.argv[1] not in cli):
        print >>sys.stderr, commandline.format_cmdlist(cli)
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "help":
        if len(sys.argv) != 3 or sys.argv[2] not in cli:
            # The user wants help, but for a command I don't know about
            print >>sys.stderr, commandline.format_cmdlist(cli)
        else:
            # The user wants help for a specific command
            print >>sys.stderr, commandline.format_cmd_help(cli[sys.argv[2]])
        sys.exit(1)

    args = sys.argv[2:]
    metadata = cli[cmd]

    # Wrong number of arguments for this command, dingus!
    if len(args) != len(metadata.args):
        print >>sys.stderr, commandline.format_cmd_help(metadata)
        sys.exit(1)

    # Ah, finally we can actually get some work done.
    init()
    metadata.func(*args)


if __name__ == "__main__":
    main()

