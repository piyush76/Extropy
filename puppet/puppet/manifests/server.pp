class puppet::server inherits puppet {
    include yum::server
    include mongrel
    include postgres

    package {
        [puppet-server, rubygem-rails]:
            ensure => installed;
    }

    file {
        fileserver-conf:
            name => "/etc/puppet/fileserver.conf",
            source => "puppet:///puppet/fileserver.conf",
            owner => "root",
            group => "root",
            require => Package[puppet-server];

        "/var/log/puppet/clients":
            ensure => directory,
            owner => "puppet",
            group => "puppet",
            require => Package[puppet-server];

        "/var/lib/puppet/plugins":
            source => "puppet:///puppet/plugins",
            owner => "root",
            group => "root",
            recurse => true,
            purge => true,
            force => true,
            require => Package[puppet-server];

        # Hack for making storeconfigs work with Rails 2.x
        "/usr/lib/ruby/site_ruby/1.8":
            source => "puppet:///puppet/overlay",
            owner => "root",
            group => "root",
            recurse => true,
            notify => Runit::Service["puppetmaster"],
            require => Package[puppet-server];

        "hannibal-executable":
            name => "/usr/local/bin/hannibal",
            source => "puppet:///puppet/hannibal",
            owner => "root",
            group => "root",
            mode => 755,
            notify => Runit::Service["hannibal"];
    }

    runit::service {
        puppetmaster:
            startdown => false,
            subscribe_ => [Package[puppet], Package[puppet-server], File[puppet-config], File[fileserver-conf]],
            before => Runit::Service["httpd"],
            notify => Runit::Service["httpd"],
            command => 'exec /usr/sbin/puppetmasterd --color=false -v 2>&1';

        hannibal:
            startdown => false,
            before => Runit::Service[puppetmaster],
            require => [File["hannibal-executable"], Package["python-m1"]],
            command => "
while :
do
    env PATH=\$PATH:/usr/bin:/usr/local/bin:/opt/python25/bin hannibal sync $hannibal_server $hannibal_port
    /bin/sleep 60
done
";
    }

    exec {
        servercert:
            command => "/usr/sbin/puppetca --generate $fqdn",
            creates => "/var/lib/puppet/ssl/certs/${fqdn}.pem",
            before => Runit::Service["httpd"],
    }

    postgres::role {
        puppet:
            ensure => present,
            password => "gibberish",
            require => Package[postgresql-server],
    }

    postgres::database {
        puppet:
            ensure => present,
            owner => puppet,
            require => Postgres::Role[puppet],
    }
}
