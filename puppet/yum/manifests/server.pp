class yum::server {
    package {
        [thttpd, rsync, createrepo]: ensure => installed,
    }

    runit::service {
        "thttpd":
            startdown => false,
            require => Package[thttpd],
            command => '
exec /usr/sbin/thttpd -D -C /etc/thttpd.conf -p 81
'
    }
}
