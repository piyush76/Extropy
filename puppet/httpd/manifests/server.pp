class httpd::server {
    package {
	[httpd, mod_ssl]: 
            ensure => installed,
            notify => Runit::Service["httpd"];
    }

    runit::service {
        "httpd": 
            startdown => false,
            require => [Package[httpd], Package[mod_ssl]],
            command => '
exec env HTTPD_LANG="C" /usr/sbin/httpd -DNO_DETACH 2>&1
'
    }

    File { owner => "root", group => "root" }
    file {
        "/etc/httpd/conf/ssl.crt":
            ensure => directory,
            mode => "700",
            require => Package["httpd"];

        "/etc/httpd/conf/ssl.key":
            ensure => directory,
            mode => "700",
            require => Package["httpd"];

        "/etc/httpd/conf/ssl.crt/messageone.com.crt":
            require => [Package["httpd"], Package["mod_ssl"], File["/etc/httpd/conf/ssl.crt"]],
            source => "puppet:///config/ssl/messageone.com.crt",
            mode => "644",
            notify => Runit::Service["httpd"];

        "/etc/httpd/conf/ssl.key/messageone.com.key":
            require => [Package["httpd"], Package["mod_ssl"], File["/etc/httpd/conf/ssl.key"]],
            source => "puppet:///config/ssl/messageone.com.key",
            mode => "644",
            notify => Runit::Service["httpd"];

        "/etc/httpd/conf.d/ssl.conf":
            require => Package["httpd"],
            source => "puppet:///httpd/ssl.conf";
    }
}
