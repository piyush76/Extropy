class postgres::reload {
    exec {
        "postgres-reload":
            command => "/usr/bin/pg_ctl reload -D /var/lib/pgsql/data",
            user => "postgres",
            refreshonly => true;
    }
}
