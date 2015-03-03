class mongrel_httpd inherits httpd::server {
    # When using mongrel, you can't start Apache without having mongrel already
    # running. Apache will still start, but it will never send requests to
    # mongrel (even if you later start mongrel). This is dumb, but it is what
    # it is...
    Runit::Service[httpd] {
        command => '
sv -w 60 start puppetmaster || exit 1
sleep 5
exec env HTTPD_LANG="C" /usr/sbin/httpd -DNO_DETACH 2>&1
'
    }
}

class mongrel {
    include mongrel_httpd

    package { 
        rubygem-mongrel: 
            ensure => installed, 
            require => Package[httpd],
    }

    file {
        "/etc/httpd/conf.d/mongrel.conf":
            content => template("mongrel/mongrel_httpd.conf"),
            notify => Runit::Service["httpd"],
            # The SELINUX portmap should be updated before we drop a new config in place,
            # to ensure that httpd will restart correctly.
            require => [Selinux::Openport[http_p8140], Selinux::Openport[http_p8001]],
    }

    selinux::openport {
        http_p8140:
            service => "http",
            port => 8140;

        http_p8001:
            service => "http",
            port => 8001;
    }
}
