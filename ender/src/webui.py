import web, sys, os, subprocess, json

urls = (
    "/sv/([-\.\w]+)/([-\.\w]+)", "svc_cmd",
    "/sv/([-\.\w]+)", "svc_cmd",
    "/sv", "svc_allstatus",
)

def log(msg):
    print >>sys.stderr, msg

def services():
    '''Iterator yielding all launch-controllable services
    '''
    for f in os.listdir("/var/service"):
	if os.path.islink(os.path.join("/var/service", f)):
	    yield f

def runcmd(cmd, service, predicate=None):
    '''Use runit to execute command "cmd" on service "service".

    cmd => start, stop, restart, status, once, restart_if_up

    predicate => function that operates on a dictionary representing the status
    information for a service. The dictionary is of the form:

        service => name of the service
        retcode => return code of the sv command
        stdout => standard output of the sv command
        stderr => standard error of the sv command
        running => 0 or 1 indicating if the service is running or not

    If the predicate returns False, then we don't execute "cmd" on "service".
    Instead, we just return the result of the status command.
    '''
    if predicate is not None:
        status = runcmd("status", service)
        if not predicate(status):
            return status
            
    c = ["/sbin/sv", "-w", "60", cmd, service]
    p = subprocess.Popen(c, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    log("PID %d: %s" % (p.pid, " ".join(c)))
    retcode = p.wait()
    out, err, running = "", "", 0
    if p.stdout is not None: out = p.stdout.read().strip()
    if p.stderr is not None: err = p.stderr.read().strip()
    log("PID %d: returned %d" % (p.pid, retcode))
    if retcode != 0:
	log("PID %d: %s %s" % (p.pid, out, err))
    if out.startswith("ok: run: ") or out.startswith("run: "):
        running = 1
    return {"service":service, "retcode":retcode, "stdout":out, "stderr":err, "running":running}

def render(obj):
    '''Serialize the given object to JSON, and print it out
    '''
    web.header('Content-Type', 'text/plain')
    print json.write(obj)

class svc_allstatus:
    '''Return a JSON dictionary representing the status of all the services
    running on this host.
    '''
    def GET(self):
	status = {}
	for service in services():
	    status[service] = runcmd("status", service)

	output = {}
	for k, v in status.items():
            output[k] = v
	render(output)

class svc_cmd:
    '''Return a JSON dictionary representing the status of a service after
    executing a runit command on it.
    '''
    def GET(self, service, cmd="status"):
        valid_cmds = {"start": "start", 
                      "stop": "force-stop",
                      "restart": "force-restart",
                      "status": "status",
                      "once": "once",
                      "restart_if_up": ("restart", lambda status: status["running"] == 1)}

	if cmd not in valid_cmds.keys() or service not in services():
	    web.notfound()
	    return

	log("%s %s issued by %s" % (service, cmd, web.ctx.ip))
    
        actual_cmd = valid_cmds[cmd]
        if type(actual_cmd) is tuple:
            render({service: runcmd(actual_cmd[0], service, actual_cmd[1])})
        else:
            render({service: runcmd(actual_cmd, service)})

def serve_forever(port):
    # Hack needed to let webpy's WSGI server listen on alternate port. Ugh.
    sys.argv[1:] = [port]
    web.webapi.internalerror = web.debugerror
    web.run(urls, globals())
