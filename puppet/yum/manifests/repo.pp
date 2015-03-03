define yum::repo($source) {
    $basedir = "/var/www/thttpd/html/yum-$name"
    $rpmdir = "$basedir/rpms"

    file {
        "$basedir":
            ensure => directory,
            require => Package[thttpd];

        "$rpmdir":
            ensure => directory,
            source => $source,
            recurse => true,
            purge => true,
            notify => Exec["createrepo-$name"],
            require => File[$basedir];
    }

    exec {
	"createrepo-$name":
            command => "/usr/bin/createrepo $basedir",
            refreshonly => true,
            require => Package[createrepo],
    }
}
