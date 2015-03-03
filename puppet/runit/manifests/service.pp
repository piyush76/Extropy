# Abstraction for setting up services using runit
#
# Prerequisites: you must have "runit" available as a package for your OS, and
# it is currently hard-coded that services are mastered in /etc/sv and runit
# uses /var/service for service discovery.
#
# Usage is pretty simple:
#
# runit::service {
#   "tomcat":
#       command => "exec /opt/tomcat/bin/catalina.sh run"
# }
#
# This will:
# 1) create a service directory called "tomcat" in /etc/sv
# 2) create an auto-rotating logging daemon specifically for this service
# 3) symlink in the new service into /var/service, runit's service location
# directory
# 4) create a Puppet "service" object representing this daemon, so you can use
# subscribe/notify with a runit service.
# 5) create the actual run script for this service, complete with proper
# double-forking
#
# Eventually, this define should be removed and replaced with a more robust
# custom type that automatically handles all of this gobbledy-gook.
#
# PARAMETERS:
#
# command => the command to start this daemon. This command (unless you use
# "rawcommand", below) will run via /bin/bash. You must supply a command that
# runs in the foreground, and it must replace the current shell (meaning: use
# "exec"). Otherwise, runit cannot do proper service supervision and you might
# as well go back to crappy init scripts.
#
# rawcommand => use the value of $command, unmodified. Use this if you want
# full control over the contents of the run script.
#
# startdown => by default, when services are created runit won't automatically
# start them. If you do indeed desire auto-start, then set this to false.
#
define runit::service($command, $rawcommand=false, $startdown=true, $subscribe_=false) {
    File { owner => "root", group => "root" }
    $servicedir = "/etc/sv/$name"

    # Create the service directory and run script
    file {
        "$servicedir":
            ensure => directory,
            require => Package[runit];

        "$servicedir/run":
            mode => "700",
            require => File[$servicedir],
            notify => Exec["restart-$name"],
            content => $rawcommand ? {
                true => "$command",
                false => "#! /bin/bash
exec 2>&1
echo Starting $name
$command
",
            };
    }

    # runit checks for the presence of a file called "down" in your service
    # directory. If it exists, then it will NOT start the service
    # automatically. Instead, the service is considered "normally down".
    if $startdown {
        file {
            "$servicedir/down":
                mode => "700",
                require => File[$servicedir],
                content => "";
        }
    }

    # Setup logging
    file {
        "$servicedir/log":
            ensure => directory,
            require => File["$servicedir"];

        "$servicedir/log/run":
            mode => "700",
            content => "#!/bin/sh
exec /usr/bin/logger -i -t svc-$name
",
            notify => Exec["restart-log-$name"],
            require => File["$servicedir/log"];
    }

    # Now create an init.d compatible script, and register a service
    file {
        "/etc/init.d/$name":
            ensure => "/sbin/sv",
            require => Service["$name"];
    }

    service {
        $name:
            provider => runit,
            require => [Package[runit], File["$servicedir/log/run"], File["$servicedir/run"]],
            enable => true;
    }

    exec {
        "restart-$name":
            command => "/sbin/sv force-restart $name",
            onlyif => "/sbin/sv status $name | /bin/grep \"^run: $name:\"",
            subscribe => $subscribe_ ? {
                false => [],
                default => $subscribe_,
            },
            refreshonly => true;

        "restart-log-$name":
            command => "/sbin/sv force-restart $name/log",
            refreshonly => true;
    }
}
