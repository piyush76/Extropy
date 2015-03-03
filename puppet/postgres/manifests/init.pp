class postgres {
    package { [postgresql, ruby-postgres, postgresql-server]: ensure => installed }

    file {
        pg_hba:
            name => "/var/lib/pgsql/data/pg_hba.conf",
            source => "puppet:///postgres/pg_hba.conf",
            owner => postgres,
            group => postgres,
            mode => 600,
    }

    service { 
        postgresql:
            ensure => running,
            enable => true,
            hasstatus => true,
            subscribe => [Package[postgresql-server], Package[postgresql], File[pg_hba]]
    }
}
