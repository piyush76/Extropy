from __future__ import with_statement
import sys, os, time, threading, workqueue
import json, commandline, utils, webui
import color as C
from commandline import expose_to_shell

@expose_to_shell("status")
def status():
    '''Query the status of all services running on each host.
    '''
    docmd(None, None)

@expose_to_shell("start")
def start(service):
    '''Start a service on each host

    service         Which service to start
    '''
    docmd(service, "start")

@expose_to_shell("restart")
def restart(service):
    '''Restart a service on each host

    service         Which service to restart
    '''
    docmd(service, "restart")

@expose_to_shell("restart-if-up")
def restart_if_up(service):
    '''Restart a service on each host, but only if the service is currently
    running.

    service         Which service to conditionally restart
    '''
    docmd(service, "restart_if_up")

@expose_to_shell("stop")
def stop(service):
    '''Stop a service on each host

    service         Which service to stop
    '''
    docmd(service, "stop")

@expose_to_shell("once")
def once(service):
    '''Start a service on each host, but don't restart it once it exits

    service         Which service to run once
    '''
    docmd(service, "once")

@expose_to_shell("http-serve")
def serve():
    '''Start a remote-control listener on port 9022
    '''
    webui.serve_forever("9022")

@expose_to_shell("with-joblist")
def with_joblist():
    '''Read launch control jobs from stdin and execute them in order

    The input is expected to look like so:

    host service command
    host service command
    host service command
    ...

    Any whitespace between the characters is okay, we're smart enough to just
    figure it out. "command" is basically any operation that the launch control
    system can support. Examples: start, stop, restart, once

    Ordering is preserved. We'll execute your joblist in order, from top to
    bottom, one line at a time. This makes execution of joblists slower than
    normally executing commands, but that's the price you pay for strict
    ordering. :)

    Here's an example joblist:

    machine1.foo.com puppetmaster stop
    machine1.foo.com httpd stop
    machine1.foo.com puppetmaster start
    machine1.foo.com httpd start
    machine2.foo.com postfix restart
    machine3.foo.com tomcat stop
    '''
    joblist = [line.split() for line in sys.stdin.read().splitlines()]
    maxhostlength = max([len(job[0]) for job in joblist])
    lock = threading.Lock()
    def onhostcomplete(host, results):
        with lock: print_results(maxhostlength, host, results)
    # To preserve order-of-operations, we'll execute the joblist with
    # a single worker thread
    results = run_jobs(joblist, onhostcomplete, 1)

def parse_hosts():
    '''Read list of hosts from stdin, and return the list

    Each line is split on whitespace, to support supplying multiple hosts per
    line of input
    '''
    lines = sys.stdin.read().splitlines()
    results = []
    for line in lines:
        results += line.split()
    return results

def run_jobs(joblist, callback, nthreads=20):
    '''Execute the given joblist, invoking "callback()" when a host is complete

    joblist => list of tuples of the form (host, service, command). If service
        is None, then we assume that you want status for all services running
        on the host

    callback => invoked as callback(host, results) whenever we successfully
        complete a remote command for a given host. The callback should be
        threadsafe!
    '''
    def worker(job):
        host, service, cmd = job
        if cmd is None:
            url = "/sv"
        else:
            url = "/sv/%s/%s" % (service, cmd)
        try:
            return utils.jsonrpc(host, 9022, url)
        except Exception, e:
            return {service: e}
    wq = workqueue.WorkQueue([worker for i in range(nthreads)])
    for job in joblist:
        wq.enqueue(job[0], job)
    for host, results in wq:
        callback(host, results)    

def docmd(service, cmd):
    '''Create a joblist that performs "cmd" for a service on all hosts.

    This will print the results to the screen.
    '''
    hosts = parse_hosts()
    maxhostlength = max(map(len, hosts))
    joblist = [(host, service, cmd) for host in hosts]
    lock = threading.Lock()
    def onhostcomplete(host, results):
        with lock: print_results(maxhostlength, host, results)
    results = run_jobs(joblist, onhostcomplete)

def print_results(maxhostlength, host, results):
    '''Print the result of a remote operation on a given host.

    maxhostlength => basically, this is a number that says how "wide" the
        host column is in the screen output

    host => which host we've just gottent results for

    results => dictionary containing results of a remote ender operation
    '''
    for service in sorted(results.keys()):
        md = results[service]
        # "Wide-formatted" version of hostname, servicename, and a generic ERROR string
        h, s, e = ("%-"+str(maxhostlength)+"s") % host, "%-20s" % service, "%-20s" % "ERROR"
        line = "%s %s %s"

        if isinstance(md, Exception):
            error = str(md)
            if C.has_colors(sys.stdout):
                args = (C.c(h), C.y(e), C.y(error))
            else:
                args = (h, e, error)
        else:
            o = md["stdout"]
            if C.has_colors(sys.stdout):
                if md["running"]:
                    args = (C.c(h), C.g(s), o)
                else:
                    args = (C.c(h), C.r(s), o)
            else:
                args = (h, s, o)
        print line % args

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
    metadata.func(*args)


if __name__ == "__main__":
    main()
