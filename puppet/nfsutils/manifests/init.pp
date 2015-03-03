class nfsutils::bootstrap {
    service {
        nfs:
            ensure => running,
            enable => true;
    }
}
