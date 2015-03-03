define selinux::openport($service, $port, $protocol=tcp) {
    $objname = "${service}_port_t"
    $selinux_is_on = "/usr/bin/test -e /usr/sbin/semanage -a -e /usr/sbin/sestatus -a -e /usr/sbin/selinuxenabled && /usr/sbin/selinuxenabled"
    $num_already_open_ports = "/usr/sbin/semanage port -l | /bin/egrep -c '^${objname}(_[^ ]*)? .*[ ,]${port}(,|$)'"

    exec {
        "addport-$name-$port":
            command => "/usr/sbin/semanage port -a -t ${objname} -p $protocol $port",
	    onlyif => "$selinux_is_on && /usr/bin/test \$($num_already_open_ports) -eq 0";
    }
}
