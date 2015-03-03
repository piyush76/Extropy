import hannibal, json, web, sys, os

urls = (
    "/profile/(.*)", "profile",
    "/status", "status",
)

ERROR_NO_SUCH_SERVER = {"errorno": 100, "error": "no such server"}

def log(msg):
    print >>sys.stderr, msg

def render(txt):
    web.header('Content-Type', 'text/plain')
    print txt

class status:
    def GET(self):
        render("Ok.")

class profile:
    def GET(self, server):
        manifests, bundles, servers = hannibal.parse_manifests(), hannibal.parse_bundles(), hannibal.parse_servers()
        if server in servers:
            metadata = servers[server]
            output = {}
            m = metadata["manifest"]
            output["manifest"] = {"name": m, "git-uri": manifests[m]}
            output["bundles"] = [{"name": b, "git-uri": bundles[b]} for b in metadata["bundles"]]
            render(json.write(output))
        else:
            render(json.write(ERROR_NO_SUCH_SERVER))

def serve_forever(port):
    # Hack needed to let webpy's WSGI server listen on alternate port. Ugh.
    sys.argv[1:] = [port]
    web.webapi.internalerror = web.debugerror
    web.run(urls, globals())
