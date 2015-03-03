class yum::fixcaching {
    text::append_if_no_such_line {
        "disable-caching":
            file => "/etc/yum.conf",
            line => "http_caching=none";
    }
}
