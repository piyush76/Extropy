define nfsutils::mount($host, $remotepath, $options="rw", $ensure=mounted) {
    file {
        $name:
            ensure => directory;
    }

    mount {
        $name:
            fstype => "nfs",
            device => "$host:$remotepath",
            options => $options,
            require => File[$name],
            ensure => $ensure;
    }
}
