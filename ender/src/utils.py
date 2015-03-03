import sys, subprocess, json, httplib

def log(msg):
    print >>sys.stderr, msg

def simple_exec(cmd, cwd=None, input=None):
    '''Execute "cmd" using a subshell, and return (pid, return code, stdout, stderr)

    input => string representing standard input. Optional.
    cwd   => working directory to use when executing "cmd". Optional, but
             if you pass it in you better be sure it exists!
    '''
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    pid = p.pid
    if input is not None:
        p.stdin.write(input)
        p.stdin.close()
    retcode = p.wait()
    log("pid=%d ret=%d cmd=%s" % (pid, retcode, str(cmd)))
    out, err = "", ""
    if p.stdout is not None: out = p.stdout.read().strip()
    if p.stderr is not None: err = p.stderr.read().strip()
    if retcode != 0:
        log("pid=%d err=%s" % (pid, err))
    return (pid, retcode, out, err)

def jsonrpc(host, port, url):
    '''Return the JSON object returned by doing an HTTP request to host:port/url

    If the returned object has an "error" attribute, we raise an exception.
    '''
    conn = httplib.HTTPConnection(host, port)
    conn.request("GET", url)
    resp = conn.getresponse()
    if resp.status != 200:
        raise RuntimeError("Got HTTP %s: %s" % (resp.status, resp.reason))
    obj = json.read(resp.read())
    return obj
