class runit {
    package {
        ["runit", "python-m1"]:
            ensure => installed;
    }

    file {
        "/usr/local/bin/ender":
            owner => "root",
            group => "root",
            source => "puppet:///runit/ender",
            notify => Runit::Service["ender"];
    }

    runit::service {
        "ender":
            startdown => false,
            require => [Package["python-m1"], File["/usr/local/bin/ender"]],
            command => '
PATH=$PATH:/opt/python25/bin 
exec /usr/local/bin/ender http-serve 2>&1
';
    }
}
