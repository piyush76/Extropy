define yum::client($server) {
    yumrepo {
        $name:
            gpgcheck => 0,
            enabled => 1,
            descr => $name,
            baseurl => "http://$server:81/yum-$name";
    }
}
