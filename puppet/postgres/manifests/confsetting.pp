define postgres::confsetting($value) {
    include postgres::reload
    text::ensure_key_value {
        "postgresql.conf-setting-$name":
            file => "/var/lib/pgsql/data/postgresql.conf",
            key => $name,
            value => $value,
            delimeter => " = ",
            notify => Exec["postgres-reload"];
    }
}
