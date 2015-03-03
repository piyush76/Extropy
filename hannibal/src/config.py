from path import path

datadir = path("/var/lib/hannibal")
manifests_file = datadir / "manifests.json"
bundles_file = datadir / "bundles.json"
servers_file = datadir / "servers.json"
local_path = datadir / "sync"
manifest_dir = local_path / "manifest"
modules_dir = local_path / "modules"
plugin_dir = modules_dir / "puppet" / "files" / "plugins"
gitcmd = "git"
