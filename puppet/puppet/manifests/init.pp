class puppet {
    include runit
    include yum::fixcaching

    package {
	puppet:
	    ensure => installed;

        ruby-shadow:
            ensure => installed,
    }

    file {
        puppet-config:
            name => "/etc/puppet/puppet.conf",
            content => template("puppet/puppet.conf"),
            require => Package[puppet];

        lockrun:
            name => "/usr/local/bin/lockrun",
            source => "puppet:///puppet/lockrun",
            owner => "root",
            group => "root",
            mode => "755";
    }

    runit::service {
	puppet:
	    startdown => false,
            subscribe_ => [Package[puppet], File[puppet-config]],
            command => $fqdn ? {
                $servername => '
while :
do
    /usr/sbin/puppetd --color=false -v -o 2>&1
    /bin/sleep 300
done
',
                default     => '
while :
do
    /usr/sbin/puppetd --color=false -v -o 2>&1
    /bin/sleep 1800	
done
',
            };
    }
}
