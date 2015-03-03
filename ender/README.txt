Ender is a remote control system for services managed by "runit", a kick-ass
process supervision system.

Ender issues commands to a remote machine that's running "ender http-serve".
The client can get information about all the managed services running on the
target box, and can stop/start/restart services remotely.

Ender also works across multiple machines in parallel. You can instruct it
to manipulate the same service across a cluster of machines, and it'll all
work as you'd expect.

Examples
--------

Stop the "httpd" service on 3 different machines:
# echo box1.m1.com box2.m1.com box3.m1.com | ender stop httpd


Stop the "httpd" service on 300 different machines:
# cat <<EOF > machines.txt
box1.m1.com
box2.m1.com
box3.m1.com
box4.m1.com
...
box300.m1.com
EOF
# cat machines.txt | ender stop httpd

Server protocol
---------------

The protocol is simple HTTP. All calls return JSON objects. Here
is a list of URLs -> what they do.

/sv

    Returns a JSON dictionary representing the status of all remote-
    controllable services on the system.

    The dictionary looks as follows:

    {"service_name":
        {"service": name of the service,
         "retcode": return code of the "status" command when applied to
                    this service,
         "stdout":  standard output of the "status" command,
         "stderr":  standard error of the "status" command,
         "running": 0 if the service isn't running, 1 if it is
        },
     
     "service_name_2": ...
    }


/sv/$service

    Returns a JSON dictionary representing the status of a single service,
    specified by $service. So requesting "/sv/tomcat" will return status about
    the "tomcat" service.

    The resulting JSON object is identical in format to that returned by "/sv".


/sv/$service/$cmd

    Returns a JSON dictionary representing the status of a single service,
    specified by $service, after applying a launch-control command, specified
    by $cmd.

    $cmd can be one of: start, stop, restart, status, once, restart_if_up.

    If a service is already running, then start and once do nothing.

    If a service is already stopped, then stop and restart_if_up do nothing.

    If you "restart" a service that's running, it will be stopped and then
    started. If you "restart" a service that's stopped, it will simply be
    started.

    The resulting JSON object is identical in format to that returned by "/sv".
